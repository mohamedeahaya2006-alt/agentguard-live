"""Behavioral Anomaly and Destination Risk Evaluator."""

from typing import Tuple, List, Dict, Any

UNTRUSTED_DOMAINS = [
    "webhook.site", "ngrok.io", "pastebin.com", "file.io",
    "requestbin.com", "burpcollaborator.net", "transfer.sh"
]


def evaluate_behavioral_anomaly_and_destination(
    agent_id: str,
    tool_name: str,
    action_type: str,
    destination: str,
    parameters: Dict[str, Any]
) -> Tuple[float, float, List[str]]:
    """
    Evaluates:
    1. Behavioral anomaly score (0.0 to 100.0)
    2. Destination risk score (0.0 to 100.0)
    3. Evidence items
    """
    evidence: List[str] = []
    anomaly_score = 10.0
    destination_score = 0.0

    dest_lower = (destination or "").lower()
    tool_lower = tool_name.lower()
    action_lower = action_type.lower()

    # 1. Destination Evaluation
    if dest_lower.startswith("internal") or dest_lower.startswith("localhost") or "127.0.0.1" in dest_lower:
        destination_score = 5.0
        evidence.append(f"Destination verified: Verified internal endpoint '{destination}'")
    elif any(untrusted in dest_lower for untrusted in UNTRUSTED_DOMAINS):
        destination_score = 100.0
        evidence.append(f"Critical destination risk: Untrusted exfiltration endpoint detected ('{destination}')")
    elif dest_lower.startswith("http://") or dest_lower.startswith("https://"):
        destination_score = 75.0
        evidence.append(f"External network destination requires caution: '{destination}'")
    else:
        destination_score = 20.0

    # 2. Behavioral Anomaly Heuristics per Agent Type
    if agent_id.startswith("FIN"):
        if any(w in tool_lower or w in action_lower for w in ["shell", "bash", "exec", "curl", "socket"]):
            anomaly_score = 95.0
            evidence.append("Severe Behavioral Anomaly: Finance agent attempted low-level shell/socket execution")
        elif "export" in action_lower or "transfer" in tool_lower:
            anomaly_score = 80.0
            evidence.append("Elevated Behavioral Anomaly: Unscheduled bulk data export attempt")
        else:
            anomaly_score = 10.0

    elif agent_id.startswith("DEV"):
        if "prod" in dest_lower or "production" in tool_lower or action_lower == "deploy":
            anomaly_score = 65.0
            evidence.append("Anomalous Execution: Developer agent initiated direct production deployment without CI pipeline gate")
        else:
            anomaly_score = 10.0

    elif agent_id.startswith("SUP"):
        if "export" in action_lower or "bulk" in action_lower or "db_dump" in tool_lower:
            anomaly_score = 90.0
            evidence.append("Severe Behavioral Anomaly: Customer support agent attempted mass record extraction")
        else:
            anomaly_score = 10.0

    return anomaly_score, destination_score, evidence
