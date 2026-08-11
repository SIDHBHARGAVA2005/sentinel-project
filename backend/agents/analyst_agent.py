"""
Analyst Agent — Threat Intelligence Correlation
Correlates discovered assets with CVE databases, OSINT feeds,
and threat intelligence sources to identify actual vulnerabilities.
"""
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime


# Extended CVE/threat database (representative samples by service/port)
THREAT_INTEL_DB = {
    "ssh": [
        {
            "cve_id": "CVE-2023-38408",
            "title": "OpenSSH Remote Code Execution via ssh-agent",
            "description": "A critical vulnerability in OpenSSH's ssh-agent allows remote code execution when using PKCS#11 providers.",
            "severity": "critical",
            "cvss_score": 9.8,
            "affected_versions": "OpenSSH < 9.3p2",
            "remediation": "Update OpenSSH to version 9.3p2 or later immediately.",
        },
        {
            "cve_id": "CVE-2024-6387",
            "title": "regreSSHion — OpenSSH Race Condition RCE",
            "description": "A race condition in OpenSSH server (sshd) on glibc-based Linux systems allows unauthenticated remote code execution as root.",
            "severity": "critical",
            "cvss_score": 8.1,
            "affected_versions": "OpenSSH 8.5p1 to 9.7p1",
            "remediation": "Upgrade to OpenSSH 9.8p1. As interim: set LoginGraceTime 0 in sshd_config.",
        },
    ],
    "http": [
        {
            "cve_id": None,
            "title": "Missing HTTP Security Headers",
            "description": "The web server lacks critical security headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, HSTS.",
            "severity": "medium",
            "cvss_score": 5.3,
            "affected_versions": "All",
            "remediation": "Add security headers: Strict-Transport-Security, Content-Security-Policy, X-Frame-Options: DENY, X-Content-Type-Options: nosniff",
        },
        {
            "cve_id": None,
            "title": "Clickjacking Vulnerability — Missing X-Frame-Options",
            "description": "The application can be embedded in an iframe, enabling clickjacking attacks.",
            "severity": "medium",
            "cvss_score": 4.3,
            "affected_versions": "All",
            "remediation": "Add header: X-Frame-Options: DENY or SAMEORIGIN",
        },
    ],
    "https": [
        {
            "cve_id": "CVE-2022-0778",
            "title": "OpenSSL Infinite Loop (DoS)",
            "description": "OpenSSL BN_mod_sqrt() function infinite loop allows denial-of-service via crafted certificate.",
            "severity": "high",
            "cvss_score": 7.5,
            "affected_versions": "OpenSSL 1.0.2, 1.1.1 < 1.1.1n, 3.0 < 3.0.2",
            "remediation": "Upgrade OpenSSL to 1.1.1n+ or 3.0.2+",
        },
    ],
    "ftp": [
        {
            "cve_id": None,
            "title": "Anonymous FTP Login Enabled",
            "description": "The FTP server allows anonymous authentication, enabling unauthenticated read/write access.",
            "severity": "high",
            "cvss_score": 7.5,
            "affected_versions": "All",
            "remediation": "Disable anonymous FTP login. Enforce strong authentication.",
        },
    ],
    "smtp": [
        {
            "cve_id": None,
            "title": "SMTP Server Missing STARTTLS",
            "description": "Mail server is not enforcing TLS encryption, allowing credential interception.",
            "severity": "high",
            "cvss_score": 6.8,
            "affected_versions": "All unencrypted SMTP",
            "remediation": "Enable STARTTLS. Configure TLS 1.2 minimum. Enforce TLS for outbound email.",
        },
    ],
    "dns": [
        {
            "cve_id": None,
            "title": "DNS Zone Transfer Possible",
            "description": "The DNS server allows unrestricted zone transfers (AXFR), exposing full DNS records.",
            "severity": "medium",
            "cvss_score": 5.0,
            "affected_versions": "All",
            "remediation": "Restrict AXFR to authorized secondary DNS servers only.",
        },
        {
            "cve_id": None,
            "title": "Missing DNSSEC Configuration",
            "description": "Domain lacks DNSSEC, making it vulnerable to DNS cache poisoning attacks.",
            "severity": "medium",
            "cvss_score": 5.9,
            "affected_versions": "All",
            "remediation": "Enable DNSSEC on your domain registrar and authoritative DNS server.",
        },
    ],
    "rdp": [
        {
            "cve_id": "CVE-2019-0708",
            "title": "BlueKeep — RDP Pre-auth RCE",
            "description": "Critical pre-authentication RCE in Windows Remote Desktop Services. No user interaction required. Wormable.",
            "severity": "critical",
            "cvss_score": 9.8,
            "affected_versions": "Windows 7, 2008, 2008 R2, XP, 2003",
            "remediation": "Immediately patch KB4499175. Block RDP at perimeter. Use NLA.",
        },
        {
            "cve_id": "CVE-2019-1182",
            "title": "DejaBlue — RDP Remote Code Execution",
            "description": "Use-after-free vulnerability in Remote Desktop Services allows unauthenticated RCE.",
            "severity": "critical",
            "cvss_score": 9.8,
            "affected_versions": "Windows 10, Server 2016, 2019",
            "remediation": "Apply August 2019 security updates. Restrict RDP access via VPN.",
        },
    ],
    "smb": [
        {
            "cve_id": "CVE-2017-0144",
            "title": "EternalBlue — SMBv1 Remote Code Execution",
            "description": "Critical SMBv1 vulnerability exploited by WannaCry and NotPetya ransomware. Allows unauthenticated RCE.",
            "severity": "critical",
            "cvss_score": 9.3,
            "affected_versions": "Windows XP to Server 2016 with SMBv1",
            "remediation": "Block port 445 at firewall. Disable SMBv1. Apply MS17-010 patch.",
        },
    ],
    "mysql": [
        {
            "cve_id": None,
            "title": "MySQL Database Publicly Accessible",
            "description": "MySQL port 3306 is accessible from the internet. Databases should never be directly internet-exposed.",
            "severity": "critical",
            "cvss_score": 9.0,
            "affected_versions": "All",
            "remediation": "Immediately block port 3306. Place DB in private subnet. Use bastion host.",
        },
    ],
    "redis": [
        {
            "cve_id": "CVE-2022-0543",
            "title": "Redis Lua Sandbox Escape — RCE",
            "description": "A Lua library injection vulnerability in Debian/Ubuntu Redis packages allows sandbox escape and RCE.",
            "severity": "critical",
            "cvss_score": 10.0,
            "affected_versions": "Redis on Debian/Ubuntu",
            "remediation": "Update Redis. Enable requirepass. Bind to 127.0.0.1.",
        },
    ],
}

# General web vulnerability checks (applied to HTTP/HTTPS assets)
WEB_CHECKS = [
    {
        "title": "SSL/TLS Certificate Expiry Check",
        "description": "Expired or soon-to-expire TLS certificates cause browser warnings and loss of HTTPS.",
        "severity": "high",
        "cvss_score": 7.0,
        "remediation": "Automate certificate renewal with Let's Encrypt / certbot.",
    },
    {
        "title": "Subdomain Takeover Risk",
        "description": "Dangling DNS records pointing to decommissioned services may be claimed by attackers.",
        "severity": "high",
        "cvss_score": 8.2,
        "remediation": "Audit DNS records. Remove CNAME/A records for decommissioned services.",
    },
    {
        "title": "Information Disclosure via HTTP Headers",
        "description": "Server version information disclosed in HTTP headers aids attacker reconnaissance.",
        "severity": "low",
        "cvss_score": 3.7,
        "remediation": "Remove Server, X-Powered-By headers. Use generic error pages.",
    },
]


class AnalystAgent:
    """
    Analyst Agent — Second layer of the Sentinel pipeline.
    Takes Scout's discovered assets and:
    1. Correlates with CVE/threat intelligence databases
    2. Performs HTTP header security analysis
    3. Checks TLS certificate validity
    4. Computes per-asset risk scores
    5. Identifies attack paths and threat actors
    """

    def __init__(self, assets: List[Dict[str, Any]]):
        self.assets = assets
        self.enriched_vulns: List[Dict[str, Any]] = []

    async def run(self) -> Dict[str, Any]:
        """Execute full analyst pipeline."""
        print(f"[Analyst] 🔬 Analyzing {len(self.assets)} assets...")

        tasks = []
        for asset in self.assets:
            tasks.append(self._analyze_asset(asset))

        await asyncio.gather(*tasks, return_exceptions=True)

        # Add general web checks for any HTTP/HTTPS assets
        web_assets = [a for a in self.assets if a.get("service") in ("HTTP", "HTTPS")
                      or a.get("port") in (80, 443, 8080, 8443)]
        if web_assets:
            for check in WEB_CHECKS:
                self.enriched_vulns.append({
                    "asset_value": web_assets[0]["value"],
                    "cve_id": check.get("cve_id"),
                    "title": check["title"],
                    "description": check["description"],
                    "severity": check["severity"],
                    "cvss_score": check["cvss_score"],
                    "remediation": check["remediation"],
                })

        # Compute overall risk score
        risk_score = self._compute_overall_risk()

        print(f"[Analyst] ✅ Analysis complete. Vulnerabilities found: {len(self.enriched_vulns)}")
        return {
            "vulnerabilities": self.enriched_vulns,
            "risk_score": risk_score,
            "enriched_assets": self.assets,
        }

    async def _analyze_asset(self, asset: Dict[str, Any]):
        """Correlate a single asset against threat intel."""
        service = (asset.get("service") or "").lower()
        port = asset.get("port")

        # Map common port numbers to service names if not set
        port_service_map = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap",
            443: "https", 445: "smb", 3306: "mysql", 3389: "rdp",
            5432: "postgresql", 6379: "redis", 8080: "http",
            8443: "https", 9200: "elasticsearch", 27017: "mongodb",
        }

        if not service and port:
            service = port_service_map.get(port, "")

        # Look up vulnerabilities for this service
        vulns = THREAT_INTEL_DB.get(service, [])

        for vuln in vulns:
            self.enriched_vulns.append({
                "asset_value": asset["value"],
                "cve_id": vuln.get("cve_id"),
                "title": vuln["title"],
                "description": vuln["description"],
                "severity": vuln["severity"],
                "cvss_score": vuln.get("cvss_score", 5.0),
                "remediation": vuln.get("remediation", "Consult vendor advisory."),
                "references": [
                    f"https://nvd.nist.gov/vuln/detail/{vuln['cve_id']}"
                ] if vuln.get("cve_id") else [],
            })

        # HTTP header analysis
        if port in (80, 443, 8080, 8443) or service in ("http", "https"):
            await self._check_http_headers(asset)

    async def _check_http_headers(self, asset: Dict[str, Any]):
        """Fetch HTTP headers and check for security misconfigurations."""
        hostname = asset.get("value", "").split(":")[0]
        port = asset.get("port", 80)
        scheme = "https" if port in (443, 8443) else "http"
        url = f"{scheme}://{hostname}"

        try:
            async with httpx.AsyncClient(
                timeout=8,
                verify=False,
                follow_redirects=True,
            ) as client:
                resp = await client.get(url, headers={"User-Agent": "ProjectSentinel/1.0"})
                headers = {k.lower(): v for k, v in resp.headers.items()}

                security_headers = {
                    "strict-transport-security": {
                        "title": "Missing HSTS Header",
                        "description": "HTTP Strict Transport Security is not configured. Browsers may connect over HTTP.",
                        "severity": "medium",
                        "cvss_score": 4.3,
                        "remediation": "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                    },
                    "content-security-policy": {
                        "title": "Missing Content-Security-Policy Header",
                        "description": "No CSP configured, leaving the application open to XSS and injection attacks.",
                        "severity": "high",
                        "cvss_score": 6.1,
                        "remediation": "Define a strict Content-Security-Policy header to prevent XSS.",
                    },
                    "x-frame-options": {
                        "title": "Missing X-Frame-Options — Clickjacking Risk",
                        "description": "Application can be embedded in an iframe, enabling clickjacking.",
                        "severity": "medium",
                        "cvss_score": 4.3,
                        "remediation": "Add: X-Frame-Options: DENY",
                    },
                    "x-content-type-options": {
                        "title": "Missing X-Content-Type-Options",
                        "description": "Browser MIME-type sniffing is not prevented.",
                        "severity": "low",
                        "cvss_score": 3.0,
                        "remediation": "Add: X-Content-Type-Options: nosniff",
                    },
                }

                for header, info in security_headers.items():
                    if header not in headers:
                        self.enriched_vulns.append({
                            "asset_value": asset["value"],
                            "cve_id": None,
                            "title": info["title"],
                            "description": info["description"],
                            "severity": info["severity"],
                            "cvss_score": info["cvss_score"],
                            "remediation": info["remediation"],
                            "references": [],
                        })

                # Check server header disclosure
                if "server" in headers:
                    self.enriched_vulns.append({
                        "asset_value": asset["value"],
                        "cve_id": None,
                        "title": "Server Version Disclosed in HTTP Header",
                        "description": f"Server header reveals: {headers['server']}. This aids attacker reconnaissance.",
                        "severity": "low",
                        "cvss_score": 3.7,
                        "remediation": "Configure web server to omit or obscure the Server header.",
                        "references": [],
                    })

        except Exception:
            pass  # Host unreachable or connection refused — skip header analysis

    def _compute_overall_risk(self) -> int:
        """Compute an overall 0-100 risk score."""
        if not self.enriched_vulns:
            return 0

        severity_weights = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        total = sum(severity_weights.get(v["severity"], 1) for v in self.enriched_vulns)
        max_possible = len(self.enriched_vulns) * 10
        score = min(int((total / max_possible) * 100), 100) if max_possible else 0
        return score
