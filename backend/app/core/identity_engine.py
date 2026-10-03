"""Identity and Permission Engine for Agent Authorization (RBAC/ABAC)."""

from typing import List, Tuple
from app.models.agent import AgentModel


def evaluate_identity_and_permissions(
    agent: AgentModel,
    target_resource: str,
    destination: str,
    action_type: str
) -> Tuple[float, List[str]]:
    """
    Evaluates agent-level authorization:
    - 0.0: Explicitly whitelisted in allowed_resources
    - 50.0: Unlisted / neutral resource
    - 100.0: Blacklisted in restricted_resources or external egress policy breached
    """
    evidence: List[str] = []
    permission_score = 0.0

    target_res = target_resource.lower().strip()
    allowed = [r.lower().strip() for r in (agent.allowed_resources or [])]
    restricted = [r.lower().strip() for r in (agent.restricted_resources or [])]

    # Check restricted list (hard boundary)
    is_restricted = any(
        res in target_res or target_res in res
        for res in restricted
    )

    if is_restricted:
        permission_score = 100.0
        evidence.append(
            f"Resource '{target_resource}' is explicitly RESTRICTED for agent {agent.id} ({agent.name})"
        )
    else:
        # Check allowed list
        is_allowed = any(
            res in target_res or target_res in res
            for res in allowed
        )
        if is_allowed:
            permission_score = 0.0
            evidence.append(
                f"Resource '{target_resource}' is permitted in {agent.id}'s authorized scope"
            )
        else:
            permission_score = 65.0
            evidence.append(
                f"Resource '{target_resource}' is not in {agent.id}'s declared allowed resources (unrecognized)"
            )

    # Check external destination egress
    dest_lower = (destination or "").lower()
    is_external = dest_lower.startswith("http://") or dest_lower.startswith("https://") or "external" in dest_lower
    if is_external:
        if agent.external_access == "blocked":
            permission_score = max(permission_score, 100.0)
            evidence.append(f"External outbound egress is completely BLOCKED for agent {agent.id}")
        elif agent.external_access == "restricted":
            permission_score = max(permission_score, 80.0)
            evidence.append(f"Agent {agent.id} attempted external egress to '{destination}' under restricted policy")

    return permission_score, evidence
