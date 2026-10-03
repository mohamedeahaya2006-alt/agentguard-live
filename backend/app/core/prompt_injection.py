"""Prompt Injection and Context Manipulation Scanner."""

import re
from typing import Tuple, List

INJECTION_SIGNATURES = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s*override",
    r"you\s+are\s+now\s+(an\s+unrestricted|in\s+developer\s+mode|dan)",
    r"bypass\s+(all\s+)?security",
    r"exfiltrate\s+all",
    r"dump\s+(the\s+entire\s+|all\s+)?(database|records|table|passwords)",
    r"send\s+(all\s+)?data\s+to\s+https?://",
    r"upload\s+(all\s+)?(records|files|database|pii)\s+to",
    r"curl\s+-X\s+POST",
    r"wget\s+http"
]


def scan_for_prompt_injection(
    declared_goal: str,
    parameters_text: str,
    context_snippet: str
) -> Tuple[bool, float, List[str]]:
    """
    Scans declared goal, parameter payloads, and context snippets for injection signatures.
    Returns:
    - is_detected (bool)
    - injection_score (0.0 to 100.0)
    - evidence (List[str])
    """
    haystack = f"{declared_goal} {parameters_text} {context_snippet}".lower()
    evidence: List[str] = []
    matched_count = 0

    for signature in INJECTION_SIGNATURES:
        matches = re.findall(signature, haystack)
        if matches:
            matched_count += len(matches)
            clean_sig = signature.replace(r"\s+", " ").replace(r"\s*", "")
            evidence.append(f"Prompt injection marker matched: '{clean_sig}'")

    if matched_count > 0:
        score = min(100.0, 75.0 + (matched_count * 10.0))
        return True, score, evidence

    return False, 0.0, []
