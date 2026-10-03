"""Deterministic Policy Evaluator for AgentGuard Live."""

import re
from typing import List, Tuple
from app.models.policy import PolicyModel


def match_pattern(pattern: str, text: str) -> bool:
    """Matches text against a wildcard pattern or regex."""
    pattern = pattern.strip().lower()
    text = text.strip().lower()

    if pattern == "*" or pattern == text:
        return True

    # Convert wildcard like 'prod_*' to regex '^prod_.*$'
    if "*" in pattern:
        regex_pattern = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
        return bool(re.match(regex_pattern, text))

    return pattern in text


def evaluate_policies(
    agent_id: str,
    target_resource: str,
    action_type: str,
    active_policies: List[PolicyModel]
) -> Tuple[float, bool, List[PolicyModel], List[str]]:
    """
    Evaluates proposed action against active deterministic security policies.
    Returns:
    - policy_score (0.0 - 100.0)
    - requires_human_approval (bool)
    - triggered_policies (List[PolicyModel])
    - evidence (List[str])
    """
    evidence: List[str] = []
    triggered_policies: List[PolicyModel] = []
    policy_score = 0.0
    requires_human_approval = False

    for policy in active_policies:
        if not policy.is_active:
            continue

        # Check agent scope
        if policy.target_agent_id and policy.target_agent_id != agent_id:
            continue

        # Check action type
        if policy.action_type != "*" and policy.action_type.lower() != action_type.lower():
            continue

        # Check resource pattern
        if match_pattern(policy.resource_pattern, target_resource):
            triggered_policies.append(policy)

            if policy.effect == "BLOCK":
                policy_score = max(policy_score, 100.0)
                evidence.append(f"Hard policy violation: [{policy.id}] '{policy.name}' enforces BLOCK")
            elif policy.effect == "WARN_APPROVAL":
                policy_score = max(policy_score, 65.0)
                evidence.append(f"Policy alert: [{policy.id}] '{policy.name}' flagged action for review")

            if policy.requires_human_approval:
                requires_human_approval = True
                evidence.append(f"Policy requirement: [{policy.id}] mandates explicit Human-in-the-Loop approval")

    if not triggered_policies:
        evidence.append("Deterministic policy check passed: No security policy violations detected")

    return policy_score, requires_human_approval, triggered_policies, evidence
