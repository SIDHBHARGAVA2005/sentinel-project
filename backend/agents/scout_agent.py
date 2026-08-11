"""
Scout Agent — External Asset Discovery
Discovers subdomains, IPs, open ports, and services for a given target domain.
Uses DNS enumeration, certificate transparency logs, and optional Shodan API.
"""
import asyncio
import socket
import ssl
import json
import random
import ipaddress
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

from core.config import settings


# Common subdomains to probe (OSINT wordlist)
COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "admin", "api", "dev", "staging", "test",
    "shop", "blog", "portal", "vpn", "remote", "webmail", "smtp",
    "pop", "imap", "ns1", "ns2", "cdn", "static", "assets", "media",
    "app", "mobile", "m", "support", "help", "docs", "wiki", "status",
    "monitor", "dashboard", "login", "auth", "sso", "gitlab", "jenkins",
    "jira", "confluence", "grafana", "kibana", "db", "database", "mysql",
    "redis", "elasticsearch", "backup", "old", "legacy", "beta", "prod",
    "production", "internal", "corp", "intranet", "private", "secure",
    "gateway", "proxy", "fw", "firewall", "router", "switch", "mgmt",
]

# Common ports to check
COMMON_PORTS = [
    (21, "FTP"), (22, "SSH"), (23, "Telnet"), (25, "SMTP"),
    (53, "DNS"), (80, "HTTP"), (110, "POP3"), (143, "IMAP"),
    (443, "HTTPS"), (445, "SMB"), (3306, "MySQL"), (3389, "RDP"),
    (5432, "PostgreSQL"), (6379, "Redis"), (8080, "HTTP-Alt"),
    (8443, "HTTPS-Alt"), (9200, "Elasticsearch"), (27017, "MongoDB"),
]

# Known service vulnerability patterns
SERVICE_VULN_MAP = {
    "FTP": {"title": "FTP Service Exposed", "severity": "high",
             "description": "FTP transmits data in plaintext. Credentials can be intercepted.",
             "cvss": 7.5, "remediation": "Replace FTP with SFTP. Disable anonymous login."},
    "Telnet": {"title": "Telnet Service Detected", "severity": "critical",
                "description": "Telnet is unencrypted and severely outdated.",
                "cvss": 9.8, "remediation": "Disable Telnet immediately. Use SSH instead."},
    "SMB": {"title": "SMB Port Exposed to Internet", "severity": "critical",
             "description": "Publicly exposed SMB (445) is a major attack vector (EternalBlue/WannaCry).",
             "cvss": 9.3, "remediation": "Block port 445 at the firewall. Never expose SMB to internet."},
    "RDP": {"title": "RDP Exposed to Public Internet", "severity": "critical",
             "description": "Exposed RDP is a primary ransomware entry point.",
             "cvss": 9.8, "remediation": "Restrict RDP behind VPN. Enable NLA. Use strong credentials."},
    "MySQL": {"title": "Database Port Publicly Accessible", "severity": "critical",
               "description": "Direct database access from internet is extremely dangerous.",
               "cvss": 9.0, "remediation": "Immediately firewall database ports. Use private subnets."},
    "MongoDB": {"title": "MongoDB Exposed Without Auth", "severity": "critical",
                 "description": "Unauthenticated MongoDB is a well-known data breach vector.",
                 "cvss": 9.1, "remediation": "Enable authentication. Move to private subnet."},
    "Redis": {"title": "Redis Server Exposed", "severity": "high",
               "description": "Unauthenticated Redis allows arbitrary command execution.",
               "cvss": 8.1, "remediation": "Add authentication. Bind to 127.0.0.1 only."},
    "Elasticsearch": {"title": "Elasticsearch Cluster Exposed", "severity": "high",
                       "description": "Exposed Elasticsearch can leak sensitive indexed data.",
                       "cvss": 7.5, "remediation": "Enable X-Pack security. Restrict network access."},
    "HTTP": {"title": "Unencrypted HTTP Service", "severity": "medium",
              "description": "HTTP transmits data without encryption.",
              "cvss": 5.3, "remediation": "Enable HTTPS with valid TLS certificate. Redirect HTTP to HTTPS."},
    "SMTP": {"title": "SMTP Open Relay Check Needed", "severity": "medium",
              "description": "Misconfigured SMTP can be used as an open relay for spam.",
              "cvss": 5.0, "remediation": "Configure SPF, DKIM, DMARC. Disable open relay."},
}


class ScoutAgent:
    """
    Scout Agent — First layer of the Sentinel pipeline.
    Performs external asset discovery using:
    1. DNS subdomain enumeration
    2. Certificate Transparency log queries
    3. Port scanning on discovered IPs
    4. Shodan API (if key configured)
    """

    def __init__(self, target: str, scan_id: str):
        self.target = target.lower().strip().replace("https://", "").replace("http://", "").rstrip("/")
        self.scan_id = scan_id
        self.discovered_assets: List[Dict[str, Any]] = []
        self.discovered_vulns: List[Dict[str, Any]] = []

    async def run(self) -> Dict[str, Any]:
        """Execute full scout pipeline."""
        print(f"[Scout] 🔍 Starting discovery for: {self.target}")

        # Phase 1: Subdomain enumeration
        subdomains = await self._enumerate_subdomains()

        # Phase 2: Certificate transparency
        ct_subs = await self._query_certificate_transparency()
        all_subs = list(set(subdomains + ct_subs))

        # Phase 3: Resolve IPs
        resolved = await self._resolve_subdomains(all_subs)

        # Phase 4: Port scanning
        await self._scan_ports(resolved)

        # Phase 5: Shodan enrichment (if API key available)
        if settings.SHODAN_API_KEY:
            await self._enrich_with_shodan()

        print(f"[Scout] ✅ Discovery complete. Assets: {len(self.discovered_assets)}, Vulns: {len(self.discovered_vulns)}")
        return {
            "assets": self.discovered_assets,
            "vulnerabilities": self.discovered_vulns,
        }

    async def _enumerate_subdomains(self) -> List[str]:
        """DNS-based subdomain brute force."""
        found = []
        loop = asyncio.get_event_loop()

        async def check(sub):
            hostname = f"{sub}.{self.target}"
            try:
                result = await loop.run_in_executor(None, socket.gethostbyname, hostname)
                if result:
                    found.append(hostname)
                    return hostname, result
            except (socket.gaierror, OSError):
                pass
            return None

        tasks = [check(sub) for sub in COMMON_SUBDOMAINS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid = []
        for r in results:
            if r and not isinstance(r, Exception):
                valid.append(r[0])

        # Add the base domain itself
        try:
            loop = asyncio.get_event_loop()
            base_ip = await loop.run_in_executor(None, socket.gethostbyname, self.target)
            if base_ip:
                self.discovered_assets.append({
                    "asset_type": "domain",
                    "value": self.target,
                    "ip_address": base_ip,
                    "risk_level": "low",
                    "risk_score": 1.0,
                    "tags": ["base-domain"],
                    "raw_data": {"ip": base_ip},
                })
        except Exception:
            pass

        return valid

    async def _query_certificate_transparency(self) -> List[str]:
        """Query crt.sh for certificate transparency subdomain data."""
        subs = []
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://crt.sh/?q=%.{self.target}&output=json",
                    headers={"User-Agent": "ProjectSentinel/1.0 Security Research"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for entry in data[:100]:  # limit
                        name = entry.get("name_value", "")
                        for line in name.split("\n"):
                            line = line.strip().lower()
                            if line.endswith(f".{self.target}") and "*" not in line:
                                subs.append(line)
        except Exception as e:
            print(f"[Scout] CT log query failed: {e}")
        return list(set(subs))

    async def _resolve_subdomains(self, subdomains: List[str]) -> List[Dict]:
        """Resolve hostnames to IPs."""
        resolved = []
        loop = asyncio.get_event_loop()

        for hostname in subdomains:
            try:
                ip = await loop.run_in_executor(None, socket.gethostbyname, hostname)
                resolved.append({"hostname": hostname, "ip": ip})
                self.discovered_assets.append({
                    "asset_type": "subdomain",
                    "value": hostname,
                    "ip_address": ip,
                    "risk_level": "low",
                    "risk_score": 2.0,
                    "tags": ["subdomain", "resolved"],
                    "raw_data": {"ip": ip, "hostname": hostname},
                })
            except Exception:
                pass

        return resolved

    async def _scan_ports(self, resolved_hosts: List[Dict]):
        """TCP port scan on discovered IPs."""
        scanned_ips = set()

        for host in resolved_hosts:
            ip = host["ip"]
            hostname = host["hostname"]

            # Skip private IPs
            try:
                if ipaddress.ip_address(ip).is_private:
                    continue
            except ValueError:
                continue

            if ip in scanned_ips:
                continue
            scanned_ips.add(ip)

            open_ports = await self._tcp_scan(ip)

            for port, service in open_ports:
                asset = {
                    "asset_type": "port",
                    "value": f"{hostname}:{port}",
                    "ip_address": ip,
                    "port": port,
                    "service": service,
                    "protocol": "TCP",
                    "risk_level": self._port_risk(port, service),
                    "risk_score": self._port_risk_score(port, service),
                    "tags": [service.lower(), "open-port"],
                    "raw_data": {"ip": ip, "port": port, "service": service},
                }
                self.discovered_assets.append(asset)

                # Check for known service vulns
                if service in SERVICE_VULN_MAP:
                    v = SERVICE_VULN_MAP[service]
                    self.discovered_vulns.append({
                        "asset_value": f"{hostname}:{port}",
                        "cve_id": None,
                        "title": v["title"],
                        "description": v["description"],
                        "severity": v["severity"],
                        "cvss_score": v["cvss"],
                        "remediation": v["remediation"],
                    })

    async def _tcp_scan(self, ip: str) -> List[tuple]:
        """Async TCP connect scan."""
        open_ports = []
        loop = asyncio.get_event_loop()

        async def check_port(port, service):
            try:
                conn = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(conn, timeout=2.0)
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
                open_ports.append((port, service))
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                pass

        tasks = [check_port(p, s) for p, s in COMMON_PORTS]
        await asyncio.gather(*tasks, return_exceptions=True)
        return open_ports

    async def _enrich_with_shodan(self):
        """Enrich discovered IPs with Shodan data."""
        unique_ips = list(set(
            a["ip_address"] for a in self.discovered_assets
            if a.get("ip_address")
        ))[:5]  # limit API calls

        for ip in unique_ips:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        f"https://api.shodan.io/shodan/host/{ip}",
                        params={"key": settings.SHODAN_API_KEY},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for port_data in data.get("data", []):
                            port = port_data.get("port")
                            transport = port_data.get("transport", "TCP")
                            product = port_data.get("product", "Unknown")
                            banner = port_data.get("data", "")[:200]
                            self.discovered_assets.append({
                                "asset_type": "port",
                                "value": f"{ip}:{port}",
                                "ip_address": ip,
                                "port": port,
                                "service": product,
                                "protocol": transport.upper(),
                                "banner": banner,
                                "country": data.get("country_name"),
                                "org": data.get("org"),
                                "risk_level": "medium",
                                "risk_score": 4.0,
                                "tags": ["shodan", "enriched"],
                                "raw_data": port_data,
                            })
            except Exception as e:
                print(f"[Scout] Shodan enrichment failed for {ip}: {e}")

    def _port_risk(self, port: int, service: str) -> str:
        critical = {23, 445, 3389, 1433, 27017}
        high = {21, 3306, 5432, 6379, 9200}
        medium = {25, 110, 143, 8080}
        if port in critical or service in ("Telnet", "SMB", "RDP", "MongoDB"):
            return "critical"
        if port in high:
            return "high"
        if port in medium:
            return "medium"
        return "low"

    def _port_risk_score(self, port: int, service: str) -> float:
        risk = self._port_risk(port, service)
        return {"critical": 9.0, "high": 7.0, "medium": 5.0, "low": 2.0}[risk]
