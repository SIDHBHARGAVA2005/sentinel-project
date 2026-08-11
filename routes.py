"""
Project Sentinel — API Routes
All REST endpoints for the dashboard and agent orchestration.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from db.database import get_db
from models.scan import Scan, ScanStatus
from models.asset import Asset
from models.vulnerability import Vulnerability
from models.report import Report
from agents.scout_agent import ScoutAgent
from agents.analyst_agent import AnalystAgent
from agents.oracle_agent import OracleAgent

router = APIRouter()


# ─── Pydantic Schemas ────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target: str
    description: Optional[str] = None


class ScanResponse(BaseModel):
    id: str
    target: str
    status: str
    created_at: datetime
    total_assets: int
    total_vulns: int
    risk_score: int

    class Config:
        from_attributes = True


# ─── Background Task: Run Full Agent Pipeline ────────────────────────

async def run_scan_pipeline(scan_id: str, target: str):
    """
    Full Sentinel agent pipeline:
    Scout → Analyst → Oracle
    Runs as a background task after scan is created.
    """
    from db.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Mark as running
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()
            if not scan:
                return

            scan.status = ScanStatus.RUNNING
            await db.commit()

            # ── Phase 1: Scout Agent ──────────────────────────────────
            print(f"\n{'='*50}")
            print(f"[Sentinel] Starting scan: {target} | ID: {scan_id}")
            print(f"{'='*50}\n")

            scout = ScoutAgent(target=target, scan_id=scan_id)
            scout_results = await scout.run()

            raw_assets = scout_results["assets"]
            scout_vulns = scout_results["vulnerabilities"]

            # Save assets to DB
            db_assets = []
            for a in raw_assets:
                asset = Asset(
                    scan_id=scan_id,
                    asset_type=a.get("asset_type", "unknown"),
                    value=a.get("value", ""),
                    ip_address=a.get("ip_address"),
                    port=a.get("port"),
                    protocol=a.get("protocol"),
                    service=a.get("service"),
                    banner=a.get("banner"),
                    country=a.get("country"),
                    org=a.get("org"),
                    risk_level=a.get("risk_level", "low"),
                    risk_score=a.get("risk_score", 0.0),
                    tags=a.get("tags", []),
                    raw_data=a.get("raw_data", {}),
                )
                db.add(asset)
                db_assets.append(asset)

            await db.flush()  # get IDs

            # ── Phase 2: Analyst Agent ────────────────────────────────
            analyst = AnalystAgent(assets=raw_assets)
            analyst_results = await analyst.run()

            all_vulns = scout_vulns + analyst_results["vulnerabilities"]
            risk_score = analyst_results["risk_score"]

            # Build asset value → ID map
            asset_map = {a.value: a.id for a in db_assets}

            # Save vulnerabilities
            for v in all_vulns:
                asset_value = v.get("asset_value", "")
                asset_id = asset_map.get(asset_value)
                if not asset_id and db_assets:
                    asset_id = db_assets[0].id  # fallback to first asset

                vuln = Vulnerability(
                    asset_id=asset_id,
                    cve_id=v.get("cve_id"),
                    title=v.get("title", "Unknown Vulnerability"),
                    description=v.get("description"),
                    severity=v.get("severity", "medium"),
                    cvss_score=v.get("cvss_score"),
                    remediation=v.get("remediation"),
                    references=v.get("references", []),
                )
                db.add(vuln)

            # ── Phase 3: Oracle Agent ─────────────────────────────────
            oracle = OracleAgent(
                target=target,
                assets=raw_assets,
                vulnerabilities=all_vulns,
                risk_score=risk_score,
            )
            oracle_result = await oracle.run()

            report = Report(
                scan_id=scan_id,
                title=oracle_result.get("title", f"Security Report — {target}"),
                executive_summary=oracle_result.get("executive_summary"),
                technical_details=oracle_result.get("technical_details"),
                risk_score=risk_score,
                recommendations=oracle_result.get("recommendations", []),
                threat_actors=[t.get("name", "") for t in oracle_result.get("threat_actors", [])],
                attack_vectors=oracle_result.get("attack_vectors", []),
                remediation_plan=oracle_result.get("remediation_plan", []),
            )
            db.add(report)

            # Update scan record
            scan.status = ScanStatus.COMPLETED
            scan.completed_at = datetime.utcnow()
            scan.total_assets = len(raw_assets)
            scan.total_vulns = len(all_vulns)
            scan.risk_score = risk_score

            await db.commit()
            print(f"\n[Sentinel] ✅ Scan complete! Assets: {len(raw_assets)}, Vulns: {len(all_vulns)}, Risk: {risk_score}/100\n")

        except Exception as e:
            print(f"[Sentinel] ❌ Scan failed: {e}")
            import traceback
            traceback.print_exc()
            try:
                result = await db.execute(select(Scan).where(Scan.id == scan_id))
                scan = result.scalar_one_or_none()
                if scan:
                    scan.status = ScanStatus.FAILED
                    scan.error_message = str(e)
                    await db.commit()
            except Exception:
                pass


# ─── Scan Endpoints ───────────────────────────────────────────────────

@router.post("/scans", response_model=ScanResponse)
async def create_scan(
    body: ScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new scan and kick off the agent pipeline."""
    target = body.target.strip().lower()
    target = target.replace("https://", "").replace("http://", "").rstrip("/")

    if not target:
        raise HTTPException(status_code=400, detail="Target domain is required.")

    scan = Scan(target=target, status=ScanStatus.PENDING)
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    background_tasks.add_task(run_scan_pipeline, scan.id, target)
    return scan


@router.get("/scans", response_model=List[ScanResponse])
async def list_scans(db: AsyncSession = Depends(get_db)):
    """List all scans, newest first."""
    result = await db.execute(select(Scan).order_by(desc(Scan.created_at)).limit(50))
    return result.scalars().all()


@router.get("/scans/{scan_id}")
async def get_scan(scan_id: str, db: AsyncSession = Depends(get_db)):
    """Get full scan details including assets, vulnerabilities, and report."""
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")

    # Assets
    assets_result = await db.execute(select(Asset).where(Asset.scan_id == scan_id))
    assets = assets_result.scalars().all()

    # Vulnerabilities (via assets)
    all_vulns = []
    for asset in assets:
        vuln_result = await db.execute(
            select(Vulnerability).where(Vulnerability.asset_id == asset.id)
        )
        all_vulns.extend(vuln_result.scalars().all())

    # Report
    report_result = await db.execute(select(Report).where(Report.scan_id == scan_id))
    report = report_result.scalar_one_or_none()

    def asset_dict(a):
        return {
            "id": a.id, "asset_type": a.asset_type, "value": a.value,
            "ip_address": a.ip_address, "port": a.port, "service": a.service,
            "protocol": a.protocol, "risk_level": a.risk_level,
            "risk_score": a.risk_score, "tags": a.tags or [],
            "country": a.country, "org": a.org, "banner": a.banner,
            "discovered_at": a.discovered_at.isoformat() if a.discovered_at else None,
        }

    def vuln_dict(v):
        return {
            "id": v.id, "cve_id": v.cve_id, "title": v.title,
            "description": v.description, "severity": v.severity,
            "cvss_score": v.cvss_score, "remediation": v.remediation,
            "references": v.references or [],
            "asset_id": v.asset_id,
        }

    return {
        "id": scan.id,
        "target": scan.target,
        "status": scan.status,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "total_assets": scan.total_assets,
        "total_vulns": scan.total_vulns,
        "risk_score": scan.risk_score,
        "error_message": scan.error_message,
        "assets": [asset_dict(a) for a in assets],
        "vulnerabilities": [vuln_dict(v) for v in all_vulns],
        "report": {
            "id": report.id,
            "title": report.title,
            "executive_summary": report.executive_summary,
            "technical_details": report.technical_details,
            "risk_score": report.risk_score,
            "recommendations": report.recommendations or [],
            "threat_actors": report.threat_actors or [],
            "attack_vectors": report.attack_vectors or [],
            "remediation_plan": report.remediation_plan or [],
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        } if report else None,
    }


@router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a scan and all related data."""
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    await db.delete(scan)
    await db.commit()
    return {"message": "Scan deleted successfully."}


# ─── Dashboard Stats ──────────────────────────────────────────────────

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate statistics for the dashboard overview."""
    scans_result = await db.execute(select(Scan))
    scans = scans_result.scalars().all()

    total_scans = len(scans)
    completed = [s for s in scans if s.status == ScanStatus.COMPLETED]
    total_assets = sum(s.total_assets for s in completed)
    total_vulns = sum(s.total_vulns for s in completed)
    avg_risk = int(sum(s.risk_score for s in completed) / len(completed)) if completed else 0

    recent_scans = sorted(scans, key=lambda s: s.created_at, reverse=True)[:5]

    return {
        "total_scans": total_scans,
        "completed_scans": len(completed),
        "total_assets": total_assets,
        "total_vulnerabilities": total_vulns,
        "average_risk_score": avg_risk,
        "recent_scans": [
            {
                "id": s.id,
                "target": s.target,
                "status": s.status,
                "risk_score": s.risk_score,
                "total_assets": s.total_assets,
                "total_vulns": s.total_vulns,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in recent_scans
        ],
    }
