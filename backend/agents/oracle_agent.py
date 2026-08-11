"""
Oracle Agent — AI-Powered Risk Report Generator
Uses OpenAI GPT to generate comprehensive, human-readable security reports
from the Scout and Analyst findings.
Falls back to a deterministic template report if no API key is configured.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from core.config import settings


class OracleAgent:
    """
    Oracle Agent — Third layer of the Sentinel pipeline.
    Generates comprehensive risk reports using Generative AI.
    Produces both executive summaries and technical deep-dives.
    """

    def __init__(
        self,
        target: str,
        assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        risk_score: int,
    ):
        self.target = target
        self.assets = assets
        self.vulnerabilities = vulnerabilities
        self.risk_score = risk_score

    async def run(self) -> Dict[str, Any]:
        """Generate the full security report."""
        print(f"[Oracle] 📝 Generating risk report for {self.target}...")

        severity_counts = self._count_severities()
        top_vulns = self._get_top_vulns()
        attack_vectors = self._identify_attack_vectors()
        threat_actors = self._map_threat_actors()
        remediation_plan = self._build_remediation_plan()

        if settings.OPENAI_API_KEY or settings.GROQ_API_KEY:
            report = await self._generate_with_api(
                severity_counts, top_vulns, attack_vectors, threat_actors
            )
        else:
            report = self._generate_template_report(
                severity_counts, top_vulns, attack_vectors, threat_actors
            )

        report.update({
            "risk_score": self.risk_score,
            "threat_actors": threat_actors,
            "attack_vectors": attack_vectors,
            "remediation_plan": remediation_plan,
            "recommendations": self._build_recommendations(),
        })

        print(f"[Oracle] ✅ Report generated.")
        return report

    def _count_severities(self) -> Dict[str, int]:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in self.vulnerabilities:
            sev = v.get("severity", "low")
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def _get_top_vulns(self, n: int = 5) -> List[Dict]:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_vulns = sorted(
            self.vulnerabilities,
            key=lambda v: (severity_order.get(v.get("severity", "low"), 3), -(v.get("cvss_score") or 0))
        )
        return sorted_vulns[:n]

    def _identify_attack_vectors(self) -> List[str]:
        vectors = set()
        for v in self.vulnerabilities:
            title = v.get("title", "").lower()
            if "rdp" in title or "remote desktop" in title:
                vectors.add("Remote Desktop Protocol (RDP) — direct system access")
            if "smb" in title or "eternalblue" in title:
                vectors.add("SMB/Windows File Sharing — lateral movement & ransomware delivery")
            if "ssh" in title:
                vectors.add("SSH — remote code execution / brute-force entry")
            if "database" in title or "mysql" in title or "redis" in title or "mongodb" in title:
                vectors.add("Exposed Database — direct data exfiltration")
            if "ftp" in title:
                vectors.add("FTP — plaintext credential theft")
            if "xss" in title or "csp" in title or "content-security" in title:
                vectors.add("Web Application — Cross-Site Scripting (XSS)")
            if "clickjack" in title:
                vectors.add("Web Application — Clickjacking via iframe embedding")
            if "hsts" in title or "http" in title.lower():
                vectors.add("Network — Unencrypted HTTP traffic interception (MITM)")
            if "subdomain" in title:
                vectors.add("DNS — Subdomain Takeover")
            if "dns" in title or "zone transfer" in title:
                vectors.add("DNS — Zone Transfer / Cache Poisoning")
            if "ssl" in title or "tls" in title:
                vectors.add("TLS/SSL — Encrypted channel downgrade or certificate forgery")
            if "telnet" in title:
                vectors.add("Telnet — Plaintext protocol interception")
        return list(vectors) or ["General network reconnaissance", "Web application probing"]

    def _map_threat_actors(self) -> List[Dict[str, str]]:
        actors = []
        sev_counts = self._count_severities()

        if sev_counts["critical"] > 0:
            actors.append({
                "name": "Nation-State APT Groups",
                "motivation": "Espionage, data theft, infrastructure sabotage",
                "likelihood": "High — Critical vulnerabilities are prime APT entry points",
                "examples": "APT28 (Fancy Bear), APT41, Lazarus Group",
            })
            actors.append({
                "name": "Ransomware Operators",
                "motivation": "Financial extortion via data encryption",
                "likelihood": "High — Exposed RDP/SMB are primary ransomware vectors",
                "examples": "LockBit, BlackCat/ALPHV, Cl0p",
            })
        if sev_counts["high"] > 0:
            actors.append({
                "name": "Cybercriminal Groups",
                "motivation": "Financial gain via data theft and credential harvesting",
                "likelihood": "Medium-High",
                "examples": "FIN7, Cobalt Group",
            })
        actors.append({
            "name": "Opportunistic Script Kiddies",
            "motivation": "Notoriety, vandalism, cryptocurrency mining",
            "likelihood": "High — Automated scanners continuously probe the internet",
            "examples": "Automated Shodan/ZoomEye bots, Mirai botnet variants",
        })
        return actors

    def _build_remediation_plan(self) -> List[Dict[str, str]]:
        plan = []
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_vulns = sorted(
            self.vulnerabilities,
            key=lambda v: severity_order.get(v.get("severity", "low"), 3)
        )
        seen = set()
        for v in sorted_vulns:
            if v["title"] in seen:
                continue
            seen.add(v["title"])
            sev = v.get("severity", "low")
            timeline = {
                "critical": "Immediate — within 24 hours",
                "high": "Urgent — within 7 days",
                "medium": "Planned — within 30 days",
                "low": "Scheduled — within 90 days",
            }.get(sev, "Scheduled")
            plan.append({
                "priority": sev.upper(),
                "action": v["title"],
                "timeline": timeline,
                "remediation": v.get("remediation", "Follow vendor advisory."),
            })
        return plan[:10]

    def _build_recommendations(self) -> List[str]:
        recs = [
            "Implement a continuous External Attack Surface Management (EASM) program",
            "Adopt a Zero Trust security architecture — never trust, always verify",
            "Deploy Web Application Firewall (WAF) for all public-facing web services",
            "Enable Multi-Factor Authentication (MFA) on all remote access services",
            "Conduct regular penetration testing (quarterly) by a certified third party",
            "Establish a vulnerability management program with SLA-based patching",
            "Implement network segmentation to limit lateral movement",
            "Configure centralized SIEM for real-time threat detection and alerting",
            "Maintain an up-to-date asset inventory for all internet-facing services",
            "Train development and operations teams on secure coding and DevSecOps practices",
        ]
        return recs

    async def _generate_with_api(
        self,
        severity_counts: Dict,
        top_vulns: List[Dict],
        attack_vectors: List[str],
        threat_actors: List[Dict],
    ) -> Dict[str, Any]:
        """Use Groq or OpenAI to generate polished executive summary and technical details."""
        try:
            import openai
            
            if settings.GROQ_API_KEY:
                client = openai.AsyncOpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                )
                model_name = "llama3-8b-8192"
            else:
                client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                model_name = "gpt-3.5-turbo"

            vuln_summary = "\n".join([
                f"- [{v['severity'].upper()}] {v['title']}: {v['description'][:150]}"
                for v in top_vulns
            ])
            asset_types = list(set(a.get("asset_type", "") for a in self.assets))

            prompt = f"""You are a senior cybersecurity analyst writing a professional security assessment report.

Target: {self.target}
Scan Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Overall Risk Score: {self.risk_score}/100
Assets Discovered: {len(self.assets)} ({', '.join(asset_types)})
Vulnerability Summary:
  - Critical: {severity_counts['critical']}
  - High: {severity_counts['high']}
  - Medium: {severity_counts['medium']}
  - Low: {severity_counts['low']}

Top Vulnerabilities:
{vuln_summary}

Primary Attack Vectors: {', '.join(attack_vectors[:4])}

Write two sections:
1. EXECUTIVE SUMMARY (3-4 paragraphs, for non-technical management, clear business risk language)
2. TECHNICAL ANALYSIS (3-4 paragraphs, detailed technical findings for the security team)

Keep it professional, factual, and actionable. No fluff."""

            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            parts = content.split("TECHNICAL ANALYSIS")

            exec_summary = parts[0].replace("EXECUTIVE SUMMARY", "").replace("1.", "").strip()
            technical = parts[1].strip() if len(parts) > 1 else content

            return {
                "title": f"Security Assessment Report — {self.target}",
                "executive_summary": exec_summary,
                "technical_details": technical,
            }
        except Exception as e:
            print(f"[Oracle] OpenAI generation failed: {e}. Using template.")
            return self._generate_template_report(
                severity_counts, top_vulns, attack_vectors, threat_actors
            )

    def _generate_template_report(
        self,
        severity_counts: Dict,
        top_vulns: List[Dict],
        attack_vectors: List[str],
        threat_actors: List[Dict],
    ) -> Dict[str, Any]:
        """High-quality deterministic report when no AI API is available."""
        risk_label = (
            "CRITICAL" if self.risk_score >= 80
            else "HIGH" if self.risk_score >= 60
            else "MEDIUM" if self.risk_score >= 40
            else "LOW"
        )

        critical_count = severity_counts["critical"]
        high_count = severity_counts["high"]

        exec_summary = f"""
Project Sentinel conducted a comprehensive external attack surface assessment of {self.target} on {datetime.utcnow().strftime('%B %d, %Y')}. The automated multi-agent scan discovered {len(self.assets)} external-facing assets and identified {len(self.vulnerabilities)} security issues with an overall risk rating of {risk_label} ({self.risk_score}/100).

The assessment revealed {critical_count} critical and {high_count} high-severity vulnerabilities that pose immediate risk to the organization. Critical findings include publicly exposed administrative services, unencrypted protocols, and potential pathways for unauthorized system access. These vulnerabilities represent real-world attack vectors actively exploited by ransomware groups and nation-state threat actors.

From a business continuity perspective, exploitation of these vulnerabilities could result in data breaches, regulatory non-compliance (GDPR, PCI-DSS, ISO 27001), financial losses from ransomware, and severe reputational damage. Immediate remediation of all critical and high-severity findings is strongly recommended.

The organization should treat this assessment as the foundation for a structured vulnerability management program. Project Sentinel's continuous monitoring capability will track remediation progress and detect newly emerging threats against the attack surface over time.
""".strip()

        top_vuln_details = "\n".join([
            f"  • [{v['severity'].upper()}] {v['title']} (CVSS: {v.get('cvss_score', 'N/A')})"
            for v in top_vulns
        ])

        technical_details = f"""
Technical Findings Summary:
Sentinel's Scout Agent performed DNS subdomain enumeration, certificate transparency log analysis, and TCP port scanning across the target's internet-facing infrastructure. The Analyst Agent correlated all discovered assets against a curated threat intelligence database including known CVEs, OWASP Top 10 findings, and CIS Benchmark violations.

Top {min(5, len(top_vulns))} Findings by Severity:
{top_vuln_details}

Attack Surface Analysis:
The external attack surface of {self.target} spans {len(set(a.get('ip_address') for a in self.assets if a.get('ip_address')))} unique IP addresses hosting {len(self.assets)} distinct services. The primary attack vectors identified are: {'; '.join(attack_vectors[:4])}. These vectors represent the most likely initial access paths an attacker would leverage during a targeted intrusion campaign.

Vulnerability Correlation:
{critical_count} vulnerabilities are rated CRITICAL (CVSS 9.0+), requiring immediate patching within 24 hours. {high_count} findings are rated HIGH (CVSS 7.0-8.9), requiring remediation within 7 days. All critical findings involve internet-exposed services with known public exploits, meaning exploitation does not require advanced attacker capabilities.

Compliance Implications:
These findings likely constitute violations of PCI-DSS Requirement 6 (vulnerability management), ISO 27001 Annex A.12 (operations security), and NIST CSF PR.IP-12 (vulnerability management plan). Organizations subject to GDPR should treat exposure of personal data systems as a potential Article 33 reportable incident if exploited.
""".strip()

        return {
            "title": f"External Attack Surface Assessment — {self.target}",
            "executive_summary": exec_summary,
            "technical_details": technical_details,
        }
