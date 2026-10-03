"""SQLAlchemy Model for Human-in-the-Loop (HITL) Approvals."""

from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime
from app.database import Base


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(String(64), primary_key=True, index=True)   # UUID
    event_id = Column(String(64), nullable=False)
    agent_id = Column(String(64), nullable=False, index=True)
    action_description = Column(Text, nullable=False)
    target_resource = Column(String(128), nullable=False)
    risk_score = Column(Float, default=0.0)
    requested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="PENDING")          # "PENDING", "APPROVED", "REJECTED"
    reviewed_by = Column(String(64), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    justification = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "action_description": self.action_description,
            "target_resource": self.target_resource,
            "risk_score": round(self.risk_score, 1),
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "justification": self.justification,
        }
