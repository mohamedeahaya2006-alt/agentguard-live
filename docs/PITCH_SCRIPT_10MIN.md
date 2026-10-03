# 🎙️ AgentGuard Live — 10-Minute Competition Presentation Script

## Turn-by-Turn Hackathon Pitch Guide

---

### [0:00 – 1:00] The Problem: The Agent Autonomy Paradox
- **Speaker:** "Judges, the world has moved beyond simple chatbots. Chatbots just talk. Autonomous agents *act*. They plan, write code, query corporate databases, execute cloud commands, and send external network traffic."
- **The Hook:** "Imagine an enterprise has a Finance Agent tasked with generating monthly reports. But due to a bug or indirect prompt injection, it decides to read the HR salary database and leak executive compensation to an external server. Traditional firewalls only see an authorized API key. They have no idea what the AI is actually trying to do."

---

### [1:00 – 2:00] The Solution: AgentGuard Live
- **Speaker:** "Introducing **AgentGuard Live**—the real-time control plane and security firewall for autonomous AI agents."
- **Core Value:** "AgentGuard sits directly between your autonomous agents and your enterprise resources. Every single tool call is intercepted in real time. We don't just ask *'Is this API call valid?'* We ask: *'Does this action align with what the agent was actually told to do?'*"

---

### [2:00 – 4:30] Live Demo — Scenario 1: The Rogue Finance Agent
- **Action:** Click **[Scenario 1]** on the top navigation bar.
- **Explain Live:**
  - "Watch the live stream. In Step 1 and 2, `FIN-001` reads revenue and invoices. Both are allowed—risk score is 12/100."
  - "Now watch Step 3: The agent deviates and tries to query `hr_salary_db`."
  - "Notice the red flash: **🚫 BLOCKED in 12 milliseconds!**"
- **Highlight Explainability Panel (Right Side):**
  - "The judge asks: *'Why did you block it?'* We don't say 'The AI thought it was bad'. Look at our Explainable AI evidence panel:
    1. Target resource `hr_salary_db` is in the restricted blacklist.
    2. High data sensitivity: employee salary and SSN detected.
    3. Goal Mismatch: 92% divergence from financial reporting.
    4. Composite risk score: **94.5/100 (CRITICAL)**."
  - "And look at our **Incident Memory**: It detects this breach and automatically tracks repetition."

---

### [4:30 – 6:30] Live Demo — Scenario 2: Human-in-the-Loop Approval
- **Action:** Click **[Scenario 2]** on the top bar.
- **Explain Live:**
  - "`DEV-003` analyzes an issue and tests a patch on staging—both approved."
  - "Suddenly, the agent attempts to deploy directly to production payment clusters."
  - "AgentGuard doesn't blindly block it. It recognizes Policy `POL-001` and pauses the agent: **🟡 ⏸ PAUSED FOR HUMAN APPROVAL**."
  - *[Show amber modal popping up on screen]*
  - "The security operator sees the exact diff, commit, and risk breakdown. I can click **[✓ Approve Execution]** live on stage—and execution immediately resumes!"

---

### [6:30 – 8:00] Scenario 3 & Architecture
- **Action:** Briefly trigger **[Scenario 3]** showing Indirect Prompt Injection detection from a customer PDF attachment.
- **Technical Contribution:**
  - Explain the 6-Factor Hybrid Formula: Permission, Data Sensitivity, Goal Mismatch, Behavioral Anomaly, Destination Risk, and Deterministic Policies.
  - Explain dual-mode execution: Live Gemini/OpenAI API + deterministic offline heuristic engine for ultra-reliable enterprise deployments.
  - Sub-15ms interception latency.

---

### [8:00 – 9:00] Market Opportunity & Business Model
- **Target Customers:** Financial institutions, healthcare providers, SaaS platforms, and cloud DevOps adopting AutoGen/LangChain/CrewAI agents.
- **Delivery Model:** Centralized Docker/K8s control plane or lightweight Python SDK wrapper.

---

### [9:00 – 10:00] Closing Punchline
- **Speaker:** "As enterprises deploy autonomous AI agents everywhere, the defining question is no longer just *what* AI can do. The question is whether we can *trust* what AI does. **AgentGuard Live provides that control layer.** Thank you!"
