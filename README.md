# 🛡️ Project Sentinel
### Agentic-AI Framework for Proactive Threat Intelligence and Attack Surface Management

> Final Year Engineering Project | Cybersecurity + AI + Cloud

---

## 🚀 Quick Start (3 commands)

```bash
# 1. Install backend dependencies
cd backend && pip install -r requirements.txt

# 2. Start backend
uvicorn main:app --reload --port 8000

# 3. In a new terminal — start frontend
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173** → Enter any domain → Watch the agents work.

---

## 🤖 Agent Architecture

```
[ User Input: Target Domain ]
         │
         ▼
┌─────────────────┐
│   Scout Agent   │  DNS enum · CT logs · Port scan · Shodan
└────────┬────────┘
         │ Assets discovered
         ▼
┌─────────────────┐
│ Analyst Agent   │  CVE correlation · Header checks · Risk scoring
└────────┬────────┘
         │ Vulnerabilities + Risk score
         ▼
┌─────────────────┐
│  Oracle Agent   │  AI report generation (OpenAI GPT / built-in)
└────────┬────────┘
         │ Full security report
         ▼
┌─────────────────┐
│  React Dashboard│  Live results · Charts · PDF reports
└─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer        | Technology                              |
|--------------|-----------------------------------------|
| Backend      | Python 3.12, FastAPI, SQLAlchemy        |
| Database     | SQLite (dev) / PostgreSQL (prod)        |
| AI Agents    | LangChain-style pipeline, OpenAI GPT    |
| Frontend     | React 18, Tailwind CSS, Recharts        |
| DevOps       | Docker, Docker Compose                  |
| Cloud        | AWS EC2, RDS, S3 (production)           |
| OSINT APIs   | Shodan, crt.sh, NVD                     |

---

## 📁 Project Structure

```
sentinel/
├── backend/
│   ├── agents/
│   │   ├── scout_agent.py      # Asset discovery
│   │   ├── analyst_agent.py    # CVE correlation
│   │   └── oracle_agent.py     # AI report generation
│   ├── api/routes.py           # REST API endpoints
│   ├── models/                 # Database models
│   ├── db/database.py          # Async DB setup
│   ├── core/config.py          # Settings
│   ├── main.py                 # FastAPI entry point
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/              # Dashboard, Scans, Assets, Vulns, Reports
│       ├── components/         # Reusable UI components
│       └── utils/              # API client, helpers
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```
DATABASE_URL=sqlite+aiosqlite:///./sentinel.db
OPENAI_API_KEY=sk-...       # Optional — app works without it
SHODAN_API_KEY=...           # Optional — enhances discovery
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

- Frontend → http://localhost:3000
- Backend API → http://localhost:8000
- API Docs → http://localhost:8000/docs

---

## 📊 Features

- **External Asset Discovery** — Subdomains, IPs, open ports, services
- **Certificate Transparency** — Queries crt.sh for subdomain enumeration
- **CVE Correlation** — Maps services to known vulnerabilities
- **HTTP Security Analysis** — Checks for missing security headers
- **Risk Scoring** — 0-100 composite risk score per scan
- **AI Reports** — Executive summary + technical analysis
- **Live Dashboard** — Real-time scan progress with React + Recharts

---

## 👥 Team Members
*(Fill in your details)*

| Name | Roll No. | Branch |
|------|----------|--------|
|      |          |        |
|      |          |        |
|      |          |        |

---

*Project Sentinel — Engineering Final Year Project*
