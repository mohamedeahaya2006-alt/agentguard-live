"""Decision Engine implementing the 3-Tier Security State Machine."""

from app.config import THRESHOLD_ALLOW_MAX, THRESHOLD_WARN_MAX


def determine_decision(
    risk_score: float,
    requires_human_approval: bool,
    is_hard_policy_block: bool,
    is_prompt_injection: bool
) -> str:
    """
    Evaluates risk score and operational flags to determine the action verdict:
    - ALLOW: Safe operation within bounds (< 30.0)
    - WARN: Requires human approval / review (30.0 to 70.0 or explicit policy approval flag)
    - BLOCK: Critical threat, hard policy breach, or prompt injection (>= 70.0)
    """
    if is_hard_policy_block or is_prompt_injection or risk_score >= THRESHOLD_WARN_MAX:
        return "BLOCK"

    if requires_human_approval or (risk_score >= THRESHOLD_ALLOW_MAX and risk_score < THRESHOLD_WARN_MAX):
        return "WARN"

    return "ALLOW"
