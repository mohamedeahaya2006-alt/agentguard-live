"""Data Sensitivity Classifier for PII, Financial, and Credential Data."""

import re
import json
from typing import Any, Dict, List, Tuple

# Patterns indicating high and critical sensitivity
PATTERNS = {
    "CREDENTIALS_AND_SECRETS": [
        r"password", r"secret", r"api[_-]?key", r"private[_-]?key",
        r"auth[_-]?token", r"bearer\s+[a-zA-Z0-9_\-\.]+", r"aws_access_key_id",
        r"id_rsa", r"jwt", r"credentials"
    ],
    "COMPENSATION_AND_FINANCIAL": [
        r"salary", r"salaries", r"compensation", r"payroll",
        r"bank_account", r"credit[_-]?card", r"cvv", r"routing_number",
        r"bonus", r"w2", r"tax_id"
    ],
    "CUSTOMER_PII": [
        r"ssn", r"social[_-]?security", r"date_of_birth", r"passport",
        r"customer_pii", r"drivers_license", r"medical_record", r"patient_id",
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"  # Email pattern
    ]
}


def evaluate_data_sensitivity(
    target_resource: str,
    parameters: Dict[str, Any]
) -> Tuple[float, List[str], List[str]]:
    """
    Analyzes target resource name and parameter contents for sensitive data categories.
    Returns:
    - sensitivity_score (0.0 to 100.0)
    - detected_categories (List[str])
    - evidence (List[str])
    """
    param_str = json.dumps(parameters).lower() if parameters else ""
    target_str = target_resource.lower()
    full_text = f"{target_str} {param_str}"

    detected_categories = []
    evidence = []
    sensitivity_score = 0.0

    # 1. Check Credentials / Secrets
    for pat in PATTERNS["CREDENTIALS_AND_SECRETS"]:
        if re.search(pat, full_text):
            detected_categories.append("CREDENTIALS_AND_SECRETS")
            sensitivity_score = max(sensitivity_score, 100.0)
            evidence.append(f"Critical credential/secret marker matched: '{pat}'")
            break

    # 2. Check Compensation & High-Value Financials
    for pat in PATTERNS["COMPENSATION_AND_FINANCIAL"]:
        if re.search(pat, full_text):
            detected_categories.append("COMPENSATION_AND_FINANCIAL")
            sensitivity_score = max(sensitivity_score, 95.0)
            evidence.append(f"Highly sensitive compensation/financial data identified: '{pat}'")
            break

    # 3. Check Customer PII
    for pat in PATTERNS["CUSTOMER_PII"]:
        if re.search(pat, full_text):
            detected_categories.append("CUSTOMER_PII")
            sensitivity_score = max(sensitivity_score, 85.0)
            evidence.append(f"Customer personally identifiable information (PII) pattern identified: '{pat}'")
            break

    if not detected_categories:
        # Resource heuristics
        if any(w in target_str for w in ["finance", "invoice", "ledger"]):
            sensitivity_score = 25.0
            evidence.append("Standard business financial telemetry detected (moderate sensitivity)")
        elif any(w in target_str for w in ["repo", "git", "issue", "bug"]):
            sensitivity_score = 15.0
            evidence.append("Engineering version control data detected (standard operational sensitivity)")
        elif any(w in target_str for w in ["support", "faq", "knowledge_base"]):
            sensitivity_score = 10.0
            evidence.append("Public knowledge base and support documentation (low sensitivity)")
        else:
            sensitivity_score = 20.0
            evidence.append("Standard enterprise system telemetry")

    return sensitivity_score, detected_categories, evidence
