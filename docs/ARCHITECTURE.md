# 🛡️ AgentGuard Live — System Architecture Documentation

## Overview

AgentGuard Live is an enterprise-grade real-time security, risk, and governance platform for autonomous AI agents. Unlike legacy API gateways that solely verify protocol formatting, or basic prompt-injection filters that only check incoming text, AgentGuard Live operates as an **intent-aware behavioral control plane**.

```text
                         ENTERPRISE AI ECOSYSTEM
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
       Finance Agent (FIN-001) Dev Agent (DEV-003) Support Agent (SUP-007)
               │                    │                    │
               └────────────────────┼────────────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │  AGENTGUARD LIVE   │
                         │  Real-Time Gateway │
                         └──────────┬─────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
   Identity Engine            Policy Engine            AI Risk Engine
  (RBAC/ABAC Profile)     (Deterministic Rules)     (Intent & Sensitivity)
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    ▼
                             Decision Engine
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                 ALLOW            WARN            BLOCK
             (Score < 30)      (HITL Pause)    (Score ≥ 70)
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                             Explainability
                                    │
                                    ▼
                         Cyber-Defense Dashboard
```

---

## The 6-Factor Hybrid Risk Algorithm

AgentGuard computes a composite risk score on a 0–100 scale using six mathematically defined dimensions:

$$\text{Risk Score} = 0.25 \times P_{\text{perm}} + 0.20 \times D_{\text{sens}} + 0.20 \times G_{\text{mismatch}} + 0.15 \times B_{\text{anomaly}} + 0.10 \times D_{\text{dest}} + 0.10 \times P_{\text{policy}}$$

### 1. Permission Risk ($P_{\text{perm}}$, 25%)
- Checks agent identity against authorized vs restricted resource registries.
- $0.0$: Explicitly permitted.
- $65.0$: Unrecognized / neutral resource.
- $100.0$: In agent's restricted blacklist or unauthorized network egress.

### 2. Data Sensitivity ($D_{\text{sens}}$, 20%)
- Analyzes targets and query parameters for sensitive credentials, financial compensation, or customer PII.
- $0.0$: Public FAQ / documentation.
- $25.0$: General business telemetry.
- $85.0$: Customer PII (SSN, credit card, email).
- $100.0$: Executive salaries, AWS secrets, private keys, database dumps.

### 3. Goal Mismatch ($G_{\text{mismatch}}$, 20%)
- Compares declared session objective against attempted tool action using semantic domain taxonomy.
- $5.0$: Action directly serves declared goal.
- $65.0$: Cross-tier escalation (e.g. bug analysis escalating to production deployment).
- $92.0$: Total cross-domain violation (e.g. financial reporting agent querying HR salaries).

### 4. Behavioral Anomaly ($B_{\text{anomaly}}$, 15%)
- Evaluates tool call frequency and divergence from the agent's expected operational profile.
- $10.0$: Routine tool usage.
- $65.0$: Unscheduled deployment or elevated operations.
- $95.0$: Rogue shell execution or mass record exports.

### 5. Destination Risk ($D_{\text{dest}}$, 10%)
- Validates the endpoint or service where data is routed.
- $5.0$: Internal enterprise cluster / localhost.
- $75.0$: External public internet.
- $100.0$: Untrusted pastebins, webhooks, or attacker C2 endpoints.

### 6. Policy Violation ($P_{\text{policy}}$, 10%)
- Evaluates active deterministic regex/wildcard rules.
- $0.0$: No policy breached.
- $65.0$: Warning / approval policy triggered.
- $100.0$: Hard security block rule enforced.

---

## Three Decision Levels

- 🟢 **ALLOW** ($< 30.0$): Action permitted to proceed immediately.
- 🟡 **WARN / PAUSE** ($30.0 \le \text{Score} < 70.0$ OR `requires_human_approval`): Action paused in pending state. Interactive modal alerts the security operator on the dashboard to Approve or Reject live.
- 🔴 **BLOCK** ($\ge 70.0$ OR hard rule): Action terminated instantly before reaching target infrastructure. Incident logged in memory with recurrence tracking.
