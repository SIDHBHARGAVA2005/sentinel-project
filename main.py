import os
import socket
import ssl
import dns.resolver
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

# --- Configuration ---
load_dotenv()

app = FastAPI(
    title="Project Sentinel API", 
    description="Agentic-AI Framework for Proactive Threat Intelligence and Attack Surface Management",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Config
DEFAULT_GEMINI_API_KEY = "AIzaSyAffcBs19s4p4D9754GDS0-KmknDks_UQo" 
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or DEFAULT_GEMINI_API_KEY

class DomainRequest(BaseModel):
    domain: str

# --- UTILITY FUNCTIONS ---
def normalize_domain(domain: str) -> str:
    """Normalize domain input by removing protocol, paths, and trailing slashes"""
    domain = domain.strip()
    # Remove protocol
    if domain.startswith('http://'):
        domain = domain[7:]
    elif domain.startswith('https://'):
        domain = domain[8:]
    # Remove trailing slash and paths
    domain = domain.split('/')[0]
    # Remove www. prefix for consistency (optional)
    # domain = domain.replace('www.', '') if domain.startswith('www.') else domain
    return domain.lower()

def get_ssl_info(domain: str) -> Dict[str, Any]:
    """Analyze SSL/TLS certificate"""
    ssl_info = {
        "valid": False,
        "issuer": None,
        "subject": None,
        "expires": None,
        "days_until_expiry": None,
        "protocol": None,
        "cipher": None,
        "vulnerabilities": [],
        "error": None,
        "checked": False
    }
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                ssl_info["valid"] = True
                ssl_info["checked"] = True
                ssl_info["issuer"] = dict(x[0] for x in cert.get('issuer', []))
                ssl_info["subject"] = dict(x[0] for x in cert.get('subject', []))
                ssl_info["protocol"] = ssock.version()
                ssl_info["cipher"] = ssock.cipher()
                
                # Check expiry
                not_after = cert.get('notAfter')
                if not_after:
                    expire_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    ssl_info["expires"] = expire_date.isoformat()
                    days_left = (expire_date - datetime.now()).days
                    ssl_info["days_until_expiry"] = days_left
                    
                    if days_left < 30:
                        ssl_info["vulnerabilities"].append("SSL certificate expiring soon")
                    if days_left < 0:
                        ssl_info["vulnerabilities"].append("SSL certificate expired")
    except socket.gaierror:
        # Domain doesn't resolve - not an SSL issue
        ssl_info["error"] = "Domain does not resolve"
        ssl_info["checked"] = False
    except Exception as e:
        # SSL connection failed but domain might resolve
        ssl_info["error"] = str(e)
        ssl_info["checked"] = True  # We tried to check
    
    return ssl_info

def get_dns_records(domain: str) -> Dict[str, Any]:
    """Get comprehensive DNS records"""
    records = {
        "A": [],
        "AAAA": [],
        "MX": [],
        "TXT": [],
        "CNAME": [],
        "NS": [],
        "SPF": False,
        "DMARC": False,
        "DKIM": False
    }
    
    record_types = ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS']
    
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            for answer in answers:
                if rtype == 'TXT':
                    txt_str = str(answer).strip('"')
                    records["TXT"].append(txt_str)
                    # Check for SPF, DMARC, DKIM
                    if 'v=spf1' in txt_str.lower():
                        records["SPF"] = True
                    if 'v=dmarc1' in txt_str.lower():
                        records["DMARC"] = True
                    if 'v=dkim1' in txt_str.lower():
                        records["DKIM"] = True
                else:
                    records[rtype].append(str(answer))
        except:
            pass
    
    return records

def check_security_headers(domain: str) -> Dict[str, Any]:
    """Analyze HTTP security headers"""
    headers_info = {
        "https_redirect": False,
        "hsts": False,
        "csp": False,
        "x_frame_options": False,
        "x_content_type_options": False,
        "x_xss_protection": False,
        "strict_transport_security": False,
        "missing_headers": [],
        "security_score": 0
    }
    
    try:
        # Check HTTPS redirect
        http_response = requests.get(f"http://{domain}", timeout=5, allow_redirects=False)
        if http_response.status_code in [301, 302, 307, 308]:
            headers_info["https_redirect"] = True
            headers_info["security_score"] += 10
        
        # Check HTTPS headers
        https_response = requests.get(f"https://{domain}", timeout=5, verify=False)
        response_headers = https_response.headers
        
        if 'strict-transport-security' in response_headers:
            headers_info["hsts"] = True
            headers_info["strict_transport_security"] = True
            headers_info["security_score"] += 20
        else:
            headers_info["missing_headers"].append("Strict-Transport-Security")
        
        if 'content-security-policy' in response_headers:
            headers_info["csp"] = True
            headers_info["security_score"] += 15
        else:
            headers_info["missing_headers"].append("Content-Security-Policy")
        
        if 'x-frame-options' in response_headers:
            headers_info["x_frame_options"] = True
            headers_info["security_score"] += 10
        else:
            headers_info["missing_headers"].append("X-Frame-Options")
        
        if 'x-content-type-options' in response_headers:
            headers_info["x_content_type_options"] = True
            headers_info["security_score"] += 10
        else:
            headers_info["missing_headers"].append("X-Content-Type-Options")
        
        if 'x-xss-protection' in response_headers:
            headers_info["x_xss_protection"] = True
            headers_info["security_score"] += 5
        
    except:
        pass
    
    return headers_info

def detect_technology_stack(domain: str) -> Dict[str, Any]:
    """Detect web technologies and frameworks"""
    tech_stack = {
        "server": None,
        "framework": None,
        "cms": None,
        "cdn": None,
        "analytics": [],
        "indicators": []
    }
    
    try:
        response = requests.get(f"https://{domain}", timeout=5, verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        headers = response.headers
        
        # Server detection
        if 'server' in headers:
            tech_stack["server"] = headers['server']
            tech_stack["indicators"].append(f"Server: {headers['server']}")
        
        # Framework detection via headers
        if 'x-powered-by' in headers:
            tech_stack["framework"] = headers['x-powered-by']
            tech_stack["indicators"].append(f"Framework: {headers['x-powered-by']}")
        
        # CDN detection
        cdn_headers = ['cf-ray', 'x-amz-cf-id', 'x-served-by', 'x-cache']
        for header in cdn_headers:
            if header in headers:
                tech_stack["cdn"] = "Detected"
                break
        
        # Check response content for indicators
        content = response.text.lower()
        if 'wp-content' in content or 'wordpress' in content:
            tech_stack["cms"] = "WordPress"
        elif 'drupal' in content:
            tech_stack["cms"] = "Drupal"
        elif 'joomla' in content:
            tech_stack["cms"] = "Joomla"
        
    except:
        pass
    
    return tech_stack

# --- 1. SCOUT AGENT (Enhanced Discovery) ---
def scout_agent(domain: str) -> Dict[str, Any]:
    # Normalize domain first
    normalized_domain = normalize_domain(domain)
    print(f"[Scout] Scanning {normalized_domain} (original: {domain})...")
    data = {
        "domain": normalized_domain,
        "original_domain": domain,
        "ip": None,
        "ipv6": None,
        "subdomains": [],
        "open_ports": [],
        "dns_records": {},
        "ssl_info": {},
        "security_headers": {},
        "technology_stack": {}
    }
    
    # 1. Get IP addresses
    try:
        data["ip"] = socket.gethostbyname(normalized_domain)
    except:
        data["ip"] = "Unresolved"
    
    try:
        answers = dns.resolver.resolve(normalized_domain, 'AAAA')
        data["ipv6"] = [str(answer) for answer in answers]
    except:
        pass
    
    # 2. Enhanced Subdomain Discovery
    common_subs = ["www", "api", "mail", "dev", "test", "staging", "admin", "portal", 
                   "app", "blog", "cdn", "ftp", "mobile", "secure", "vpn", "webmail"]
    for sub in common_subs:
        try:
            target = f"{sub}.{normalized_domain}"
            dns.resolver.resolve(target, 'A')
            data["subdomains"].append(target)
        except:
            pass
    
    # 3. Comprehensive Port Scan (only if domain resolves)
    extended_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 
                      1433, 3306, 3389, 5432, 5900, 8080, 8443, 8888, 9000]
    if data["ip"] != "Unresolved":
        for port in extended_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex((data["ip"], port))
            if result == 0:
                data["open_ports"].append(port)
            sock.close()
    
    # 4. DNS Records Analysis
    data["dns_records"] = get_dns_records(normalized_domain)
    
    # 5. SSL/TLS Certificate Analysis
    data["ssl_info"] = get_ssl_info(normalized_domain)
    
    # 6. Security Headers Analysis (only if domain resolves)
    if data["ip"] != "Unresolved":
        data["security_headers"] = check_security_headers(normalized_domain)
    else:
        data["security_headers"] = {"error": "Domain does not resolve"}
    
    # 7. Technology Stack Detection (only if domain resolves)
    if data["ip"] != "Unresolved":
        data["technology_stack"] = detect_technology_stack(normalized_domain)
    else:
        data["technology_stack"] = {}
    
    return data

# --- 2. HUNTER AGENT (Deep Reconnaissance) ---
def hunter_agent(scout_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Hunter] Deep reconnaissance for {scout_data['domain']}...")
    
    findings = {
        "attack_surface": {
            "total_assets": 0,
            "exposed_services": [],
            "vulnerable_components": [],
            "attack_vectors": []
        },
        "threat_indicators": [],
        "compliance_issues": []
    }
    
    # Analyze attack surface
    findings["attack_surface"]["total_assets"] = (
        len(scout_data.get("subdomains", [])) + 
        len(scout_data.get("open_ports", [])) + 
        1  # main domain
    )
    
    # Identify exposed services
    service_ports = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        80: "HTTP",
        443: "HTTPS",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt"
    }
    
    for port in scout_data.get("open_ports", []):
        if port in service_ports:
            findings["attack_surface"]["exposed_services"].append({
                "port": port,
                "service": service_ports[port],
                "risk": "HIGH" if port in [21, 22, 23, 3306, 3389] else "MEDIUM"
            })
    
    # Check for vulnerable components
    tech_stack = scout_data.get("technology_stack", {})
    if tech_stack.get("cms") == "WordPress":
        findings["attack_surface"]["vulnerable_components"].append({
            "component": "WordPress CMS",
            "risk": "MEDIUM",
            "reason": "Known for frequent vulnerabilities"
        })
    
    # DNS-based threat indicators
    dns_records = scout_data.get("dns_records", {})
    if not dns_records.get("SPF"):
        findings["threat_indicators"].append({
            "type": "Email Security",
            "severity": "MEDIUM",
            "message": "SPF record missing - vulnerable to email spoofing"
        })
    
    if not dns_records.get("DMARC"):
        findings["threat_indicators"].append({
            "type": "Email Security",
            "severity": "HIGH",
            "message": "DMARC record missing - no email authentication policy"
        })
    
    # SSL/TLS issues
    ssl_info = scout_data.get("ssl_info", {})
    if ssl_info.get("vulnerabilities"):
        for vuln in ssl_info["vulnerabilities"]:
            findings["threat_indicators"].append({
                "type": "SSL/TLS",
                "severity": "HIGH",
                "message": vuln
            })
    
    # Security headers compliance
    sec_headers = scout_data.get("security_headers", {})
    if sec_headers.get("missing_headers"):
        findings["compliance_issues"].append({
            "category": "Security Headers",
            "issues": sec_headers["missing_headers"],
            "impact": "Reduced protection against XSS, clickjacking, and other attacks"
        })
    
    # Identify attack vectors
    if 80 in scout_data.get("open_ports", []) and 443 not in scout_data.get("open_ports", []):
        findings["attack_surface"]["attack_vectors"].append({
            "vector": "Unencrypted HTTP",
            "severity": "HIGH",
            "description": "HTTP traffic can be intercepted"
        })
    
    if not sec_headers.get("hsts"):
        findings["attack_surface"]["attack_vectors"].append({
            "vector": "Missing HSTS",
            "severity": "MEDIUM",
            "description": "Vulnerable to protocol downgrade attacks"
        })
    
    return findings

# --- 3. ANALYST AGENT (Enhanced Risk Assessment) ---
def analyst_agent(scout_data: Dict[str, Any], hunter_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Analyst] Assessing risks for {scout_data['domain']}...")
    risks = []
    risk_score = 0
    
    # Port-based risks
    critical_ports = {22: "SSH (Remote Access)", 3389: "RDP (Remote Desktop)", 
                      21: "FTP (File Transfer)", 3306: "MySQL Database", 23: "Telnet"}
    
    for port in scout_data.get("open_ports", []):
        if port in critical_ports:
            risks.append({
                "severity": "HIGH",
                "category": "Exposed Service",
                "msg": f"Critical Port Open: {port} ({critical_ports[port]})",
                "recommendation": "Restrict access via firewall and use VPN"
            })
            risk_score += 30
        elif port == 80:
            risks.append({
                "severity": "MEDIUM",
                "category": "Encryption",
                "msg": "Unencrypted HTTP (Port 80) detected. Use HTTPS.",
                "recommendation": "Redirect HTTP to HTTPS and disable port 80"
            })
            risk_score += 10
    
    # Subdomain risks
    for sub in scout_data.get("subdomains", []):
        if any(keyword in sub.lower() for keyword in ["dev", "test", "staging"]):
            risks.append({
                "severity": "MEDIUM",
                "category": "Exposed Environment",
                "msg": f"Staging environment exposed: {sub}",
                "recommendation": "Restrict access to development environments"
            })
            risk_score += 15
    
    # SSL/TLS risks (only penalize if domain resolves but SSL fails)
    ssl_info = scout_data.get("ssl_info", {})
    if scout_data.get("ip") != "Unresolved":
        # Domain resolves, check SSL
        if ssl_info.get("checked") and not ssl_info.get("valid"):
            # Domain resolves but SSL fails - this is CRITICAL
            risks.append({
                "severity": "CRITICAL",
                "category": "SSL/TLS",
                "msg": "SSL certificate invalid or missing",
                "recommendation": "Install valid SSL certificate immediately"
            })
            risk_score += 50
        elif ssl_info.get("days_until_expiry", 999) < 30:
            risks.append({
                "severity": "HIGH",
                "category": "SSL/TLS",
                "msg": f"SSL certificate expiring in {ssl_info.get('days_until_expiry')} days",
                "recommendation": "Renew SSL certificate before expiration"
            })
            risk_score += 20
    
    # Security headers risks (only check if domain resolves)
    if scout_data.get("ip") != "Unresolved":
        sec_headers = scout_data.get("security_headers", {})
        if sec_headers.get("missing_headers"):
            risks.append({
                "severity": "MEDIUM",
                "category": "Security Headers",
                "msg": f"Missing security headers: {', '.join(sec_headers['missing_headers'])}",
                "recommendation": "Implement recommended security headers"
            })
            risk_score += 15
    
    # DNS security risks (only check if domain resolves)
    if scout_data.get("ip") != "Unresolved":
        dns_records = scout_data.get("dns_records", {})
        if not dns_records.get("SPF"):
            risks.append({
                "severity": "MEDIUM",
                "category": "Email Security",
                "msg": "SPF record missing - vulnerable to email spoofing",
                "recommendation": "Add SPF record to DNS"
            })
            risk_score += 10
        
        if not dns_records.get("DMARC"):
            risks.append({
                "severity": "MEDIUM",  # Reduced from HIGH - not critical if domain doesn't resolve
                "category": "Email Security",
                "msg": "DMARC record missing - no email authentication policy",
                "recommendation": "Implement DMARC policy"
            })
            risk_score += 15  # Reduced from 20
    
    # Hunter findings integration (only if domain resolves)
    if scout_data.get("ip") != "Unresolved":
        threat_indicators = hunter_data.get("threat_indicators", [])
        for indicator in threat_indicators:
            risks.append({
                "severity": indicator.get("severity", "MEDIUM"),
                "category": indicator.get("type", "Threat Intelligence"),
                "msg": indicator.get("message", ""),
                "recommendation": "Review and remediate"
            })
            risk_score += 15 if indicator.get("severity") == "HIGH" else 10
    
    # If domain doesn't resolve, add a single informational risk
    if scout_data.get("ip") == "Unresolved":
        risks.append({
            "severity": "LOW",
            "category": "DNS Resolution",
            "msg": "Domain does not resolve to an IP address. This may indicate the domain is invalid, unreachable, or protected.",
            "recommendation": "Verify domain name is correct and domain is accessible"
        })
        risk_score = 10  # Low score for unresolved domains
    
    if not risks:
        risks.append({
            "severity": "LOW",
            "category": "General",
            "msg": "No immediate critical vectors found.",
            "recommendation": "Continue monitoring and maintain security best practices"
        })
    
    # Calculate risk level
    risk_level = "CRITICAL" if risk_score > 70 else "HIGH" if risk_score > 40 else "MEDIUM" if risk_score > 20 else "LOW"
    
    return {
        "risk_score": min(risk_score, 100),
        "risk_level": risk_level,
        "details": risks,
        "attack_surface_score": hunter_data.get("attack_surface", {}).get("total_assets", 0) * 2
    }

# --- 4. STRATEGIST AGENT (Remediation & Attack Surface Management) ---
def strategist_agent(scout_data: Dict[str, Any], analyst_data: Dict[str, Any], 
                     hunter_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[Strategist] Generating remediation strategy for {scout_data['domain']}...")
    
    strategy = {
        "immediate_actions": [],
        "short_term_recommendations": [],
        "long_term_improvements": [],
        "attack_surface_reduction": [],
        "priority_matrix": []
    }
    
    # Immediate actions (CRITICAL/HIGH severity)
    critical_risks = [r for r in analyst_data.get("details", []) 
                     if r.get("severity") in ["CRITICAL", "HIGH"]]
    
    for risk in critical_risks[:5]:  # Top 5 critical
        strategy["immediate_actions"].append({
            "action": risk.get("recommendation", "Address security issue"),
            "risk": risk.get("msg", ""),
            "impact": "High",
            "effort": "Medium"
        })
    
    # Short-term recommendations
    medium_risks = [r for r in analyst_data.get("details", []) 
                   if r.get("severity") == "MEDIUM"]
    
    for risk in medium_risks[:5]:
        strategy["short_term_recommendations"].append({
            "action": risk.get("recommendation", "Improve security posture"),
            "risk": risk.get("msg", ""),
            "timeline": "1-2 weeks"
        })
    
    # Attack surface reduction
    exposed_services = hunter_data.get("attack_surface", {}).get("exposed_services", [])
    for service in exposed_services:
        if service.get("risk") == "HIGH":
            strategy["attack_surface_reduction"].append({
                "service": service.get("service"),
                "port": service.get("port"),
                "action": f"Close port {service.get('port')} or restrict access via firewall",
                "benefit": "Reduces attack surface significantly"
            })
    
    # Long-term improvements
    strategy["long_term_improvements"] = [
        {
            "area": "Continuous Monitoring",
            "action": "Implement automated security scanning and monitoring",
            "benefit": "Proactive threat detection"
        },
        {
            "area": "Security Headers",
            "action": "Implement all recommended security headers",
            "benefit": "Enhanced protection against common web attacks"
        },
        {
            "area": "Email Security",
            "action": "Complete SPF, DKIM, and DMARC implementation",
            "benefit": "Prevent email spoofing and phishing"
        },
        {
            "area": "SSL/TLS",
            "action": "Set up automated certificate renewal",
            "benefit": "Prevent service disruption"
        }
    ]
    
    # Priority matrix
    strategy["priority_matrix"] = [
        {"priority": "P0", "items": len([r for r in critical_risks if r.get("severity") == "CRITICAL"])},
        {"priority": "P1", "items": len([r for r in critical_risks if r.get("severity") == "HIGH"])},
        {"priority": "P2", "items": len(medium_risks)},
        {"priority": "P3", "items": len([r for r in analyst_data.get("details", []) if r.get("severity") == "LOW"])}
    ]
    
    return strategy

# --- 5. ORACLE AGENT (Enhanced AI Reporting) ---
def oracle_agent(scout_data: dict, analyst_data: dict, hunter_data: dict, 
                 strategist_data: dict) -> str:
    print(f"[Oracle] Generating comprehensive threat intelligence report...")
    
    prompt = f"""
    Act as a Senior Cybersecurity Threat Intelligence Analyst. Generate a comprehensive executive report for {scout_data['domain']}.
    
    THREAT INTELLIGENCE DATA:
    - Domain: {scout_data['domain']}
    - IP Address: {scout_data.get('ip', 'Unknown')}
    - Open Ports: {scout_data.get('open_ports', [])}
    - Subdomains Discovered: {len(scout_data.get('subdomains', []))}
    - SSL/TLS Status: {'Valid' if scout_data.get('ssl_info', {}).get('valid') else 'Invalid/Missing'}
    - Security Headers Score: {scout_data.get('security_headers', {}).get('security_score', 0)}/100
    - Technology Stack: {scout_data.get('technology_stack', {}).get('cms', 'Unknown')}
    
    RISK ASSESSMENT:
    - Overall Risk Level: {analyst_data.get('risk_level', 'UNKNOWN')}
    - Risk Score: {analyst_data.get('risk_score', 0)}/100
    - Attack Surface Score: {analyst_data.get('attack_surface_score', 0)}
    - Critical Vulnerabilities: {len([r for r in analyst_data.get('details', []) if r.get('severity') == 'CRITICAL'])}
    - High Risk Issues: {len([r for r in analyst_data.get('details', []) if r.get('severity') == 'HIGH'])}
    
    ATTACK SURFACE ANALYSIS:
    - Total Assets: {hunter_data.get('attack_surface', {}).get('total_assets', 0)}
    - Exposed Services: {len(hunter_data.get('attack_surface', {}).get('exposed_services', []))}
    - Threat Indicators: {len(hunter_data.get('threat_indicators', []))}
    
    REMEDIATION STRATEGY:
    - Immediate Actions Required: {len(strategist_data.get('immediate_actions', []))}
    - Short-term Recommendations: {len(strategist_data.get('short_term_recommendations', []))}
    
    Generate a professional executive summary report with:
    1. Executive Summary (3-4 sentences summarizing the overall security posture)
    2. Key Findings (bullet points of top 3-5 critical issues)
    3. Threat Landscape (brief analysis of attack surface and threat indicators)
    4. Strategic Recommendations (top 3 prioritized actions)
    5. Risk Outlook (future considerations and monitoring recommendations)
    
    Keep it professional, concise, and actionable. Do NOT use markdown symbols like **, ##, or ###.
    Use plain text formatting with clear sections separated by line breaks.
    """
    
    try:
        response = requests.post(
            GEMINI_API_URL,
            params={"key": GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15
        )
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"[Oracle] API call failed: {e}")
    
    # Fallback report
    return f"""
EXECUTIVE THREAT INTELLIGENCE REPORT
Domain: {scout_data['domain']}

EXECUTIVE SUMMARY
Our comprehensive security assessment of {scout_data['domain']} reveals a {analyst_data.get('risk_level', 'UNKNOWN')} risk profile with a risk score of {analyst_data.get('risk_score', 0)}/100. The attack surface analysis identified {hunter_data.get('attack_surface', {}).get('total_assets', 0)} total assets and {len(hunter_data.get('attack_surface', {}).get('exposed_services', []))} exposed services requiring immediate attention.

KEY FINDINGS
- Risk Level: {analyst_data.get('risk_level', 'UNKNOWN')} (Score: {analyst_data.get('risk_score', 0)}/100)
- Open Ports: {len(scout_data.get('open_ports', []))} ports detected
- Subdomains: {len(scout_data.get('subdomains', []))} subdomains discovered
- SSL/TLS: {'Valid' if scout_data.get('ssl_info', {}).get('valid') else 'Issues Detected'}
- Security Headers: {scout_data.get('security_headers', {}).get('security_score', 0)}/100 score

THREAT LANDSCAPE
The attack surface analysis identified multiple potential attack vectors including exposed services on ports {', '.join(map(str, scout_data.get('open_ports', [])[:5]))}. {len(hunter_data.get('threat_indicators', []))} threat indicators were detected, requiring proactive security measures.

STRATEGIC RECOMMENDATIONS
1. Address {len(strategist_data.get('immediate_actions', []))} immediate critical security issues
2. Implement comprehensive security headers and SSL/TLS best practices
3. Reduce attack surface by closing unnecessary ports and restricting access

RISK OUTLOOK
Continuous monitoring and proactive threat intelligence gathering is recommended to maintain security posture. Regular assessments should be conducted to track improvements and emerging threats.
"""

# --- API ENDPOINTS ---
@app.post("/analyze/")
async def analyze_domain(request: DomainRequest):
    """Comprehensive domain threat intelligence analysis"""
    try:
        # Normalize domain input
        normalized_domain = normalize_domain(request.domain)
        
        # 1. Scout Agent - Discovery
        scout_data = scout_agent(request.domain)
        
        # 2. Hunter Agent - Deep Reconnaissance
        hunter_data = hunter_agent(scout_data)
        
        # 3. Analyst Agent - Risk Assessment
        analyst_data = analyst_agent(scout_data, hunter_data)
        
        # 4. Strategist Agent - Remediation Strategy
        strategist_data = strategist_agent(scout_data, analyst_data, hunter_data)
        
        # 5. Oracle Agent - AI-Powered Reporting
        oracle_report = oracle_agent(scout_data, analyst_data, hunter_data, strategist_data)
        
        return {
            "domain": scout_data.get("domain", normalized_domain),  # Use normalized domain
            "original_domain": request.domain,  # Keep original for reference
            "timestamp": datetime.now().isoformat(),
            "scout": scout_data,
            "hunter": hunter_data,
            "analyst": analyst_data,
            "strategist": strategist_data,
            "oracle_report": oracle_report,
            "summary": {
                "risk_level": analyst_data.get("risk_level"),
                "risk_score": analyst_data.get("risk_score"),
                "attack_surface_assets": hunter_data.get("attack_surface", {}).get("total_assets", 0),
                "critical_issues": len([r for r in analyst_data.get("details", []) if r.get("severity") == "CRITICAL"]),
                "high_issues": len([r for r in analyst_data.get("details", []) if r.get("severity") == "HIGH"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Project Sentinel API", "version": "2.0.0"}