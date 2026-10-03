"""SQLAlchemy Model for Security Incidents and Recurrence Memory."""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime
from app.database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, index=True)   # e.g., "INC-104"
    event_id = Column(String(64), nullable=True)            # Root trigger event ID
    agent_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(16), nullable=False)           # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    threat_category = Column(String(64), nullable=False)    # "UNAUTHORIZED_ACCESS", "PROMPT_INJECTION", etc.
    incident_time = Column(DateTime, default=datetime.utcnow, index=True)
    repetition_count = Column(Integer, default=1)           # Recurrence tracker
    summary = Column(Text, nullable=False)
    status = Column(String(32), default="RESOLVED")         # "OPEN", "INVESTIGATING", "RESOLVED", "BLOCKED"

    def to_dict(self):
        return {
            "id": self.id,
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "title": self.title,
            "severity": self.severity,
            "threat_category": self.threat_category,
            "incident_time": self.incident_time.isoformat() if self.incident_time else None,
            "repetition_count": self.repetition_count,
            "summary": self.summary,
            "status": self.status,
        }
