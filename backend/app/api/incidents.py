"""API Endpoints for Incidents, History, and Audit Trail."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import IncidentModel
from app.models.event import EventModel

incidents_router = APIRouter(prefix="/api/v1", tags=["Incidents & Audit Trail"])


@incidents_router.get("/incidents")
def list_incidents(
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Lists security incidents recorded by the platform with repetition tracking."""
    query = db.query(IncidentModel)
    if agent_id:
        query = query.filter(IncidentModel.agent_id == agent_id)
    if severity:
        query = query.filter(IncidentModel.severity == severity.upper())

    incidents = query.order_by(IncidentModel.incident_time.desc()).limit(limit).all()
    return [i.to_dict() for i in incidents]


@incidents_router.get("/events")
def list_events(
    agent_id: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """Returns the live audit stream of intercepted agent actions."""
    query = db.query(EventModel)
    if agent_id:
        query = query.filter(EventModel.agent_id == agent_id)
    if decision:
        query = query.filter(EventModel.decision == decision.upper())

    events = query.order_by(EventModel.timestamp.desc()).limit(limit).all()
    return [e.to_dict() for e in events]
