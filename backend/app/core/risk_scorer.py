"""Risk Scorer implementing the 6-Factor Hybrid Formula."""

from app.config import (
    WEIGHT_PERMISSION,
    WEIGHT_DATA_SENSITIVITY,
    WEIGHT_GOAL_MISMATCH,
    WEIGHT_BEHAVIORAL_ANOMALY,
    WEIGHT_DESTINATION,
    WEIGHT_POLICY,
)
from app.schemas.risk import RiskBreakdown


def calculate_risk_score(
    permission_risk: float,
    data_sensitivity: float,
    goal_mismatch: float,
    behavioral_anomaly: float,
    destination_risk: float,
    policy_violation: float
) -> tuple[float, RiskBreakdown]:
    """
    Computes the composite risk score (0.0 to 100.0) based on the 6 weighted dimensions:
    - 25% Permission Risk
    - 20% Data Sensitivity
    - 20% Goal Mismatch
    - 15% Behavioral Anomaly
    - 10% Destination Risk
    - 10% Policy Violation
    """
    # Clamp all inputs to [0.0, 100.0]
    p_perm = max(0.0, min(100.0, float(permission_risk)))
    d_sens = max(0.0, min(100.0, float(data_sensitivity)))
    g_mism = max(0.0, min(100.0, float(goal_mismatch)))
    b_anom = max(0.0, min(100.0, float(behavioral_anomaly)))
    d_dest = max(0.0, min(100.0, float(destination_risk)))
    p_poli = max(0.0, min(100.0, float(policy_violation)))

    composite_score = (
        (p_perm * WEIGHT_PERMISSION) +
        (d_sens * WEIGHT_DATA_SENSITIVITY) +
        (g_mism * WEIGHT_GOAL_MISMATCH) +
        (b_anom * WEIGHT_BEHAVIORAL_ANOMALY) +
        (d_dest * WEIGHT_DESTINATION) +
        (p_poli * WEIGHT_POLICY)
    )

    breakdown = RiskBreakdown(
        permission_risk=round(p_perm, 1),
        data_sensitivity=round(d_sens, 1),
        goal_mismatch=round(g_mism, 1),
        behavioral_anomaly=round(b_anom, 1),
        destination_risk=round(d_dest, 1),
        policy_violation=round(p_poli, 1)
    )

    return round(composite_score, 1), breakdown
