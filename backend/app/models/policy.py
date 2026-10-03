"""SQLAlchemy Model for Deterministic Security Policies."""

from sqlalchemy import Column, String, Text, Boolean
from app.database import Base


class PolicyModel(Base):
    __tablename__ = "policies"

    id = Column(String(64), primary_key=True, index=True)   # e.g., "POL-001"
    name = Column(String(128), nullable=False)                # "Block Cross-Department HR Access"
    description = Column(Text, nullable=True)
    target_agent_id = Column(String(64), nullable=True)     # Specific agent or NULL (all)
    resource_pattern = Column(String(128), nullable=False)  # regex/wildcard e.g., "hr_*", "prod_*"
    action_type = Column(String(32), nullable=False)        # "read", "write", "deploy", "*"
    effect = Column(String(32), nullable=False)             # "ALLOW", "WARN_APPROVAL", "BLOCK"
    requires_human_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_agent_id": self.target_agent_id,
            "resource_pattern": self.resource_pattern,
            "action_type": self.action_type,
            "effect": self.effect,
            "requires_human_approval": self.requires_human_approval,
            "is_active": self.is_active,
        }
