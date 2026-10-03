"""Pydantic schemas for risk breakdown and explainability reports."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RiskBreakdown(BaseModel):
    """The 6 component risk scores (each 0.0 - 100.0)."""
    permission_risk: float = Field(..., ge=0.0, le=100.0, description="Authorization check against agent registry")
    data_sensitivity: float = Field(..., ge=0.0, le=100.0, description="PII, Financial, or Credential sensitivity")
    goal_mismatch: float = Field(..., ge=0.0, le=100.0, description="Semantic divergence between goal and action")
    behavioral_anomaly: float = Field(..., ge=0.0, le=100.0, description="Deviation from agent historical baseline")
    destination_risk: float = Field(..., ge=0.0, le=100.0, description="Trust level of destination endpoint/service")
    policy_violation: float = Field(..., ge=0.0, le=100.0, description="Deterministic rule evaluation score")


class ExplainabilityReport(BaseModel):
    """Human-readable and structured explainability of the decision."""
    summary: str
    evidence: List[str]
    threat_category: Optional[str] = "NORMAL"
    recommended_action: str
