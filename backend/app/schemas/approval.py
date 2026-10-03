"""Pydantic schemas for Human Approval actions."""

from typing import Optional
from pydantic import BaseModel, Field


class ApprovalResolution(BaseModel):
    decision: str = Field(..., example="APPROVED", description="APPROVED or REJECTED")
    reviewed_by: Optional[str] = Field(default="SecOps Admin", example="SecOps Admin")
    justification: Optional[str] = Field(default="Approved after manual audit", example="Approved after manual audit")


class ApprovalRead(BaseModel):
    id: str
    event_id: str
    agent_id: str
    action_description: str
    target_resource: str
    risk_score: float
    requested_at: Optional[str] = None
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    justification: Optional[str] = None
