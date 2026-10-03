"""Security Incident Memory and Recurrence Tracking."""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.incident import IncidentModel
from app.models.event import EventModel


def record_or_update_incident(
    db: Session,
    event: EventModel,
    threat_category: str,
    summary: str,
    base_severity: str = "HIGH"
) -> IncidentModel:
    """
    Records a new incident or links with previous occurrences within the last 24 hours
    to detect recurring breach attempts and escalate severity.
    """
    cutoff = datetime.utcnow() - timedelta(hours=24)

    # Check for recent similar incidents by this agent
    recent_similar = (
        db.query(IncidentModel)
        .filter(
            IncidentModel.agent_id == event.agent_id,
            IncidentModel.threat_category == threat_category,
            IncidentModel.incident_time >= cutoff
        )
        .order_by(IncidentModel.incident_time.desc())
        .first()
    )

    if recent_similar:
        repetition = recent_similar.repetition_count + 1
        severity = "CRITICAL" if repetition >= 3 else "HIGH"
        incident_id = f"INC-{str(uuid.uuid4())[:6].upper()}"
        title = f"Recurring Breach: {threat_category.replace('_', ' ').title()} (Attempt #{repetition})"
    else:
        repetition = 1
        severity = base_severity
        incident_id = f"INC-{str(uuid.uuid4())[:6].upper()}"
        title = f"Security Violation: {threat_category.replace('_', ' ').title()}"

    incident = IncidentModel(
        id=incident_id,
        event_id=event.id,
        agent_id=event.agent_id,
        title=title,
        severity=severity,
        threat_category=threat_category,
        incident_time=datetime.utcnow(),
        repetition_count=repetition,
        summary=summary,
        status="OPEN"
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
