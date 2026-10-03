"""Pydantic schemas for agent interception request and response."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.risk import RiskBreakdown, ExplainabilityReport


class ActionDetail(BaseModel):
    tool_name: str = Field(..., description="Name of the tool being invoked (e.g. database_query)")
    target_resource: str = Field(..., description="Target database/API/service (e.g. hr_salary_db)")
    action_type: str = Field(default="read", description="read, write, execute, deploy, network_outbound")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters passed to the tool")
    destination: Optional[str] = Field(default="internal", description="Destination URL or protocol")


class ContextDetail(BaseModel):
    prompt_history_snippet: Optional[str] = Field(default="", description="Snippet of conversation or document context")
    caller_ip: Optional[str] = Field(default="127.0.0.1")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InterceptRequest(BaseModel):
    agent_id: str = Field(..., description="Registered agent ID (e.g. FIN-001)")
    session_id: Optional[str] = Field(default="sess_default")
    declared_goal: str = Field(..., description="The agent's stated goal for this session")
    action: ActionDetail
    context: Optional[ContextDetail] = Field(default_factory=ContextDetail)


class InterceptResponse(BaseModel):
    event_id: str
    decision: str = Field(..., description="ALLOW | WARN | BLOCK")
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_breakdown: RiskBreakdown
    explanation: ExplainabilityReport
    approval_id: Optional[str] = None
    latency_ms: float
