"""SQLAlchemy Model for Intercepted Agent Events and Audit Stream."""

from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from app.database import Base


class EventModel(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True, index=True)   # UUID
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    agent_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), nullable=True)
    declared_goal = Column(Text, nullable=False)
    tool_name = Column(String(64), nullable=False)
    target_resource = Column(String(128), nullable=False)
    action_type = Column(String(32), nullable=False)
    payload_preview = Column(Text, nullable=True)
    destination = Column(String(256), nullable=False)
    risk_score = Column(Float, nullable=False)              # 0.0 to 100.0
    decision = Column(String(16), nullable=False)            # "ALLOW", "WARN", "BLOCK"
    risk_breakdown = Column(JSON, nullable=False)           # 6 sub-scores
    explanation = Column(JSON, nullable=False)              # Structured reasons & evidence
    approval_status = Column(String(32), default="NONE")    # "NONE", "PENDING", "APPROVED", "REJECTED"
    latency_ms = Column(Float, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "declared_goal": self.declared_goal,
            "tool_name": self.tool_name,
            "target_resource": self.target_resource,
            "action_type": self.action_type,
            "payload_preview": self.payload_preview,
            "destination": self.destination,
            "risk_score": round(self.risk_score, 1),
            "decision": self.decision,
            "risk_breakdown": self.risk_breakdown,
            "explanation": self.explanation,
            "approval_status": self.approval_status,
            "latency_ms": round(self.latency_ms, 2),
        }
