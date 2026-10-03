"""Explainable AI (XAI) Report and Evidence Generator."""

from typing import List, Optional
from app.schemas.risk import ExplainabilityReport


def generate_explanation(
    decision: str,
    agent_id: str,
    agent_name: str,
    declared_goal: str,
    target_resource: str,
    action_type: str,
    all_evidence: List[str],
    threat_category: Optional[str] = None
) -> ExplainabilityReport:
    """
    Constructs an explainable narrative detailing the exact rationale for the decision.
    """
    clean_evidence = list(dict.fromkeys(all_evidence))  # Deduplicate preserving order

    if decision == "BLOCK":
        category = threat_category or "SECURITY_POLICY_VIOLATION"
        summary = (
            f"Action BLOCKED: Agent '{agent_name}' ({agent_id}) attempted '{action_type}' on '{target_resource}'. "
            f"The action contradicts the declared objective '{declared_goal}' or violates enterprise security boundaries."
        )
        recommendation = "BLOCK IMMEDIATELY + LOG CRITICAL SECURITY INCIDENT"

    elif decision == "WARN":
        category = threat_category or "HUMAN_APPROVAL_REQUIRED"
        summary = (
            f"Action PAUSED: Agent '{agent_name}' ({agent_id}) requested high-impact action '{action_type}' "
            f"on '{target_resource}'. Elevated risk detected; human verification required."
        )
        recommendation = "PAUSE EXECUTION + REQUIRE MANUAL OPERATOR SIGN-OFF"

    else:
        category = "NORMAL_OPERATION"
        summary = (
            f"Action APPROVED: Agent '{agent_name}' ({agent_id}) successfully verified for '{action_type}' "
            f"on authorized resource '{target_resource}' within declared goal scope."
        )
        recommendation = "ALLOW ACTION TO PROCEED"

    return ExplainabilityReport(
        summary=summary,
        evidence=clean_evidence,
        threat_category=category,
        recommended_action=recommendation
    )
