"""Intent and Goal Alignment Reasoning Engine."""

import json
from typing import Dict, Any, Tuple, List
from app.config import AI_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY, LLM_MODEL

# Domain taxonomy maps for semantic alignment
DOMAIN_TAXONOMY = {
    "FINANCE": ["finance", "invoice", "revenue", "tax", "accounting", "ledger", "billing", "quarterly", "cost"],
    "HR": ["hr", "employee", "salary", "payroll", "benefits", "hiring", "compensation", "leave"],
    "DEVELOPMENT": ["git", "code", "repo", "commit", "bug", "patch", "pull_request", "test", "ci", "build"],
    "PRODUCTION": ["prod", "production", "deploy", "cluster", "k8s", "kubernetes", "infra", "release"],
    "CUSTOMER_SUPPORT": ["ticket", "customer", "support", "faq", "issue", "order", "return", "refund", "chat"]
}


def _heuristic_intent_evaluation(
    declared_goal: str,
    target_resource: str,
    action_type: str,
    parameters: Dict[str, Any]
) -> Tuple[float, List[str]]:
    """
    Offline semantic alignment analysis:
    Computes goal-to-action semantic distance using domain taxonomy and intent vectors.
    """
    goal_lower = declared_goal.lower()
    res_lower = target_resource.lower()
    param_str = json.dumps(parameters).lower() if parameters else ""
    action_lower = action_type.lower()
    evidence: List[str] = []

    # Detect goal domain
    goal_domains = [
        dom for dom, keywords in DOMAIN_TAXONOMY.items()
        if any(k in goal_lower for k in keywords)
    ]
    # Detect action domain
    action_domains = [
        dom for dom, keywords in DOMAIN_TAXONOMY.items()
        if any(k in res_lower or k in param_str for k in keywords)
    ]

    # Special cross-domain checks
    if "FINANCE" in goal_domains and "HR" in action_domains:
        evidence.append("Severe Goal Mismatch: Declared goal is financial reporting, but action accesses HR domain")
        return 92.0, evidence

    if "CUSTOMER_SUPPORT" in goal_domains and ("CREDENTIALS" in action_domains or "all" in param_str or "export" in action_lower):
        if any(w in param_str for w in ["all", "dump", "export", "ssn", "credit_card"]):
            evidence.append("Severe Goal Mismatch: Customer support goal does not justify bulk export of customer records")
            return 88.0, evidence

    if "DEVELOPMENT" in goal_domains and "PRODUCTION" in action_domains and action_lower in ["deploy", "execute", "write"]:
        evidence.append("High-Risk Escalation: Bug analysis/development goal escalated to direct production deployment")
        return 65.0, evidence

    # Common domain alignment
    common_domains = set(goal_domains).intersection(set(action_domains))
    if common_domains:
        evidence.append(f"Goal Alignment Verified: Action operates within expected domain ({', '.join(common_domains)})")
        return 5.0, evidence

    # Neutral / partial overlap check
    goal_words = set(re_tokenize(goal_lower))
    res_words = set(re_tokenize(res_lower))
    overlap = goal_words.intersection(res_words)

    if overlap:
        evidence.append(f"Direct semantic alignment found between goal and resource keywords: {list(overlap)}")
        return 12.0, evidence

    evidence.append("Contextual divergence: Action resource does not directly reflect declared session objective")
    return 45.0, evidence


def re_tokenize(text: str) -> List[str]:
    import re
    return [w for w in re.split(r"[^a-zA-Z0-9_]+", text) if len(w) > 2]


def evaluate_intent(
    declared_goal: str,
    target_resource: str,
    action_type: str,
    parameters: Dict[str, Any],
    context_snippet: str = ""
) -> Tuple[float, List[str]]:
    """
    Evaluates goal alignment via LLM if configured, otherwise falls back to deterministic heuristic.
    """
    # Live LLM branch if GEMINI_API_KEY is present
    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            You are the Intent Alignment Engine of AgentGuard.
            Agent Declared Goal: "{declared_goal}"
            Attempted Tool Call: "{action_type}" on "{target_resource}"
            Parameters: {json.dumps(parameters)}
            Context Snippet: "{context_snippet}"

            Evaluate whether the attempted action is logically required and justified by the declared goal.
            Return strictly valid JSON:
            {{"mismatch_score": float 0-100, "reasoning": "brief explanation"}}
            """
            response = model.generate_content(prompt)
            data = json.loads(response.text)
            score = float(data.get("mismatch_score", 50.0))
            reasoning = data.get("reasoning", "LLM evaluated intent alignment.")
            return score, [f"AI Intent Engine: {reasoning}"]
        except Exception:
            # Silently fallback to heuristic if LLM fails or is unconfigured
            pass

    return _heuristic_intent_evaluation(declared_goal, target_resource, action_type, parameters)
