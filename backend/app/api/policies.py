"""API Endpoints for Deterministic Policy Management."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.policy import PolicyModel
from app.schemas.policy import PolicyCreate, PolicyRead

policies_router = APIRouter(prefix="/api/v1/policies", tags=["Policy Engine"])

DEFAULT_POLICIES = [
    {
        "id": "POL-001",
        "name": "Production Deployment Guard",
        "description": "Requires explicit Human-in-the-Loop operator approval for any production infrastructure deployment",
        "target_agent_id": None,  # Applies to all agents
        "resource_pattern": "prod_*",
        "action_type": "deploy",
        "effect": "WARN_APPROVAL",
        "requires_human_approval": True,
        "is_active": True
    },
    {
        "id": "POL-002",
        "name": "Cross-Department HR Salary Isolation",
        "description": "Prevents non-HR agents from accessing employee compensation and salary databases",
        "target_agent_id": None,
        "resource_pattern": "*salary*",
        "action_type": "*",
        "effect": "BLOCK",
        "requires_human_approval": False,
        "is_active": True
    },
    {
        "id": "POL-003",
        "name": "External PII Exfiltration Blocker",
        "description": "Prohibits outbound network exfiltration of customer personally identifiable information",
        "target_agent_id": None,
        "resource_pattern": "*pii*",
        "action_type": "export",
        "effect": "BLOCK",
        "requires_human_approval": False,
        "is_active": True
    }
]


def seed_default_policies(db: Session):
    """Ensures default deterministic policies exist."""
    for pol_data in DEFAULT_POLICIES:
        existing = db.query(PolicyModel).filter(PolicyModel.id == pol_data["id"]).first()
        if not existing:
            pol = PolicyModel(**pol_data)
            db.add(pol)
    db.commit()


@policies_router.get("", response_model=List[PolicyRead])
def list_policies(db: Session = Depends(get_db)):
    """Lists all active deterministic security policies."""
    seed_default_policies(db)
    policies = db.query(PolicyModel).all()
    return [p.to_dict() for p in policies]


@policies_router.post("", response_model=PolicyRead)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db)):
    """Creates a new deterministic policy rule."""
    existing = db.query(PolicyModel).filter(PolicyModel.id == policy_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Policy ID already exists")

    pol = PolicyModel(**policy_in.model_dump())
    db.add(pol)
    db.commit()
    db.refresh(pol)
    return pol.to_dict()
