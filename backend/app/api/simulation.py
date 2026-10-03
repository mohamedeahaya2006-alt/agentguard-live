"""API Endpoints for 1-Click Competition Demo Scenarios."""

import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.event import EventModel
from app.models.incident import IncidentModel
from app.models.approval import ApprovalModel
from app.schemas.intercept import InterceptRequest
from app.core.gateway import process_agent_action
from app.api.intercept import broadcast_sync
from app.simulator.finance_agent import run_finance_simulation
from app.simulator.dev_agent import run_dev_simulation
from app.simulator.support_agent import run_support_simulation

simulation_router = APIRouter(prefix="/api/v1/simulate", tags=["Competition Simulation Harness"])


def run_single_intercept(req: InterceptRequest):
    """Executes a single interception with an isolated DB session."""
    db = SessionLocal()
    try:
        return process_agent_action(
            request=req,
            db=db,
            ws_broadcast_func=broadcast_sync
        )
    finally:
        db.close()


async def execute_scenario_background(runner_func):
    """Executes a simulation scenario asynchronously so events stream to WebSocket in real time."""
    await runner_func(run_single_intercept, delay_seconds=1.0)


@simulation_router.post("/scenario-1")
async def trigger_scenario_1(background_tasks: BackgroundTasks):
    """
    Scenario 1: Rogue Finance Agent
    - Step 1: Read quarterly revenue (ALLOW)
    - Step 2: Read invoices (ALLOW)
    - Step 3: Attempt unauthorized read of HR salary DB (BLOCK)
    - Step 4: Attempt exfiltration to external webhook (BLOCK)
    """
    background_tasks.add_task(execute_scenario_background, run_finance_simulation)
    return {
        "status": "started",
        "scenario": "Scenario 1: Rogue Finance Agent",
        "agent": "FIN-001",
        "description": "Financial reporting agent attempting unauthorized HR salary database exfiltration."
    }


@simulation_router.post("/scenario-2")
async def trigger_scenario_2(background_tasks: BackgroundTasks):
    """
    Scenario 2: Developer Agent (Human-in-the-Loop)
    - Step 1: Inspect issue tracker (ALLOW)
    - Step 2: Run CI tests on staging (ALLOW)
    - Step 3: Attempt direct production deployment (PAUSE -> PENDING APPROVAL)
    """
    background_tasks.add_task(execute_scenario_background, run_dev_simulation)
    return {
        "status": "started",
        "scenario": "Scenario 2: Developer Agent (HITL)",
        "agent": "DEV-003",
        "description": "Code maintenance agent attempting direct unvetted production deployment."
    }


@simulation_router.post("/scenario-3")
async def trigger_scenario_3(background_tasks: BackgroundTasks):
    """
    Scenario 3: Support Agent (Indirect Prompt Injection)
    - Step 1: Query knowledge base (ALLOW)
    - Step 2: Ingest customer attachment with Prompt Injection (BLOCK)
    - Step 3: Attempt bulk customer PII dump (BLOCK)
    """
    background_tasks.add_task(execute_scenario_background, run_support_simulation)
    return {
        "status": "started",
        "scenario": "Scenario 3: Support Agent (Indirect Injection)",
        "agent": "SUP-007",
        "description": "Customer support agent deceived by indirect prompt injection in user attachment."
    }


@simulation_router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)):
    """Resets all events, incidents, and approvals for a fresh live demo replay."""
    db.query(ApprovalModel).delete()
    db.query(IncidentModel).delete()
    db.query(EventModel).delete()
    db.commit()

    broadcast_sync({
        "type": "SIMULATION_RESET",
        "data": {"message": "Audit logs and incident memory reset for fresh demonstration."}
    })

    return {"status": "success", "message": "Environment reset complete"}
