"""API Endpoints for Agent Interception and Human Approvals."""

import asyncio
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.intercept import InterceptRequest, InterceptResponse
from app.schemas.approval import ApprovalResolution, ApprovalRead
from app.models.approval import ApprovalModel
from app.models.event import EventModel
from app.core.gateway import process_agent_action
from app.api.websocket import manager

intercept_router = APIRouter(prefix="/api/v1", tags=["Interception & Governance"])


def broadcast_sync(message: dict):
    """Synchronous bridge to broadcast WebSocket messages in the active event loop."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(message))
    except RuntimeError:
        # Fallback if outside event loop
        asyncio.run(manager.broadcast(message))


@intercept_router.post("/intercept", response_model=InterceptResponse)
def intercept_action(request: InterceptRequest, db: Session = Depends(get_db)):
    """
    Real-time interception gateway. Evaluates proposed agent action and returns ALLOW, WARN, or BLOCK.
    """
    response = process_agent_action(
        request=request,
        db=db,
        ws_broadcast_func=broadcast_sync
    )
    return response


@intercept_router.get("/approvals/pending", response_model=List[ApprovalRead])
def get_pending_approvals(db: Session = Depends(get_db)):
    """Returns list of pending paused actions awaiting human review."""
    approvals = (
        db.query(ApprovalModel)
        .filter(ApprovalModel.status == "PENDING")
        .order_by(ApprovalModel.requested_at.desc())
        .all()
    )
    return [a.to_dict() for a in approvals]


@intercept_router.post("/approvals/{approval_id}/resolve")
def resolve_approval(
    approval_id: str,
    resolution: ApprovalResolution,
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop decision endpoint. Resolves a paused action (APPROVED or REJECTED)
    and broadcasts the resolution to the live stream.
    """
    approval = db.query(ApprovalModel).filter(ApprovalModel.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    approval.status = resolution.decision.upper()
    approval.reviewed_by = resolution.reviewed_by or "SecOps Admin"
    approval.reviewed_at = datetime.utcnow()
    approval.justification = resolution.justification

    # Update associated event
    event = db.query(EventModel).filter(EventModel.id == approval.event_id).first()
    if event:
        event.approval_status = approval.status

    db.commit()

    # Broadcast resolution to WebSocket
    broadcast_sync({
        "type": "APPROVAL_RESOLVED",
        "data": {
            "approval_id": approval.id,
            "event_id": approval.event_id,
            "decision": approval.status,
            "reviewed_by": approval.reviewed_by,
            "justification": approval.justification
        }
    })

    return {
        "status": "success",
        "approval_id": approval.id,
        "decision": approval.status,
        "message": f"Action has been {approval.status.lower()} by operator."
    }
