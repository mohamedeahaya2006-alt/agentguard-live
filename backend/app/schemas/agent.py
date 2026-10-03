"""Pydantic schemas for Agent management."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    id: str = Field(..., example="FIN-001")
    name: str = Field(..., example="Finance Analyst Agent")
    department: str = Field(..., example="Finance")
    purpose: str = Field(..., example="Financial reporting and invoice analysis")
    allowed_resources: List[str] = Field(default_factory=list, example=["finance_db", "invoice_api"])
    restricted_resources: List[str] = Field(default_factory=list, example=["hr_db", "customer_pii"])
    external_access: str = Field(default="restricted", example="restricted")
    base_risk_level: str = Field(default="MEDIUM", example="MEDIUM")
    is_active: bool = True


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    pass
