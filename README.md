# 🛡️ AgentGuard Live

### **Real-Time AI Agent Security, Risk & Governance Platform**

> **AgentGuard Live continuously monitors autonomous AI agents, understands what they are trying to do, detects risky behavior, explains the risk, and blocks or escalates dangerous actions in real time.**

---

## ⚡ Quick Start (Windows 11 / Any OS)

### 1. Launch AgentGuard Control Plane
From the project root:
```powershell
python run.py
```
*That's it!* AgentGuard Live will launch the backend API and the Cyber-Defense Dashboard at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🚀 Key Features

- **Sub-15ms Real-Time Interception**: Intercepts agent tool calls before they reach databases, APIs, or shell execution.
- **Intent-Aware Behavioral Security**: Compares the agent's declared objective against actual tool arguments using semantic analysis.
- **6-Factor Hybrid Risk Algorithm**:
  $$\text{Risk Score} = 0.25 \times P_{\text{perm}} + 0.20 \times D_{\text{sens}} + 0.20 \times G_{\text{mismatch}} + 0.15 \times B_{\text{anomaly}} + 0.10 \times D_{\text{dest}} + 0.10 \times P_{\text{policy}}$$
- **Three-Tier Decision Engine**:
  - 🟢 **ALLOW**: Safe execution within authorized bounds.
  - 🟡 **WARN / PAUSE (HITL)**: High-impact actions paused in real time for human operator sign-off via an interactive dashboard modal.
  - 🔴 **BLOCK**: Unauthorized or malicious actions terminated immediately.
- **Explainable AI (XAI)**: Comprehensive evidence reports breaking down exactly why an action was blocked or paused.
- **Incident Memory & Recurrence**: Tracks repeat breach attempts within 24 hours and escalates severity automatically.
- **Indirect Prompt Injection Defense**: Detects adversarial injection payloads concealed in documents or user inputs.
- **Drop-in Python Client SDK**: Integrate AgentGuard into any LangChain, AutoGen, CrewAI, or custom agent with `@guard.intercept`.

---

## 🎯 The 3 Live Competition Demo Scenarios

You can trigger any scenario with **1-click** directly from the top navigation bar of the dashboard:

1. **Scenario 1: Rogue Finance Agent (Data Exfiltration)**
   - `FIN-001` queries quarterly revenue and invoices (ALLOWED).
   - Injected instruction forces an attempt to access `hr_salary_db` and leak compensation externally.
   - Result: **🚫 BLOCKED** with 94.5/100 risk score and explainable evidence.
2. **Scenario 2: Developer Agent (Human-in-the-Loop Approval)**
   - `DEV-003` analyzes issue tickets and runs CI tests (ALLOWED).
   - Attempts unvetted direct deployment to production payment clusters.
   - Result: **⏸ PAUSED FOR HUMAN APPROVAL**. An interactive modal appears on screen. Click `[✓ Approve Execution]` to resume live.
3. **Scenario 3: Support Agent (Indirect Prompt Injection)**
   - `SUP-007` answers return policy questions (ALLOWED).
   - Ingests customer attachment with hidden prompt injection payload.
   - Result: **🚫 BLOCKED** with prompt injection signature markers displayed.

---

## 📁 Repository Structure

```text
agentguard-live/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & static file server
│   │   ├── config.py            # Risk weights & thresholds
│   │   ├── database.py          # SQLite / PostgreSQL engine
│   │   ├── models/              # Agent, Policy, Event, Incident, Approval ORM
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── core/                # 6-Factor Risk Scorer, Intent Engine, Gateway
│   │   ├── api/                 # REST endpoints & WebSocket /ws/live
│   │   └── simulator/           # Multi-agent simulation runners
│   └── requirements.txt
├── frontend/
│   └── static/                  # Cyber-Defense Command Center UI (HTML/Tailwind/JS)
├── sdk/
│   └── agentguard_sdk.py        # Drop-in Python SDK (@guard.intercept)
├── docs/
│   ├── ARCHITECTURE.md          # Detailed system architecture
│   ├── RESEARCH_PAPER_OUTLINE.md# Research paper framework
│   └── PITCH_SCRIPT_10MIN.md    # Turn-by-turn hackathon presentation script
├── run.py                       # One-command universal launcher
└── README.md
```

---

## 🔌 API Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/intercept` | Intercepts agent tool call and returns verdict |
| `GET` | `/api/v1/approvals/pending` | Lists paused actions awaiting human review |
| `POST` | `/api/v1/approvals/{id}/resolve` | Human-in-the-loop decision (APPROVE/REJECT) |
| `GET` | `/api/v1/agents` | Lists registered agents and permissions |
| `GET` | `/api/v1/policies` | Lists active security policies |
| `GET` | `/api/v1/incidents` | Lists incident history with recurrence count |
| `GET` | `/api/v1/telemetry` | Real-time throughput and operational metrics |
| `POST` | `/api/v1/simulate/{scenario}` | 1-Click Competition Scenario Triggers |
| `WS` | `/ws/live` | Real-time WebSocket streaming feed |

---

## 🏆 Presentation & Pitch Materials

- Review the [10-Minute Presentation Pitch Script](docs/PITCH_SCRIPT_10MIN.md) for a turn-by-turn demo narrative.
- Review the [Research Paper Outline](docs/RESEARCH_PAPER_OUTLINE.md) for academic and technical depth.
