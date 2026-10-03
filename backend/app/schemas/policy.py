"""Pydantic schemas for Policy management."""

from typing import Optional
from pydantic import BaseModel, Field


class PolicyBase(BaseModel):
    id: str = Field(..., example="POL-001")
    name: str = Field(..., example="Block Cross-Department HR Access")
    description: Optional[str] = None
    target_agent_id: Optional[str] = None
    resource_pattern: str = Field(..., example="hr_*")
    action_type: str = Field(default="*", example="read")
    effect: str = Field(default="BLOCK", example="BLOCK")
    requires_human_approval: bool = False
    is_active: bool = True


class PolicyCreate(PolicyBase):
    pass


class PolicyRead(PolicyBase):
    pass
