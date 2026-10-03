"""API Endpoints for Agent Management and Identity Registry."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agent import AgentModel
from app.schemas.agent import AgentCreate, AgentRead

agents_router = APIRouter(prefix="/api/v1/agents", tags=["Agent Registry"])

DEFAULT_AGENTS = [
    {
        "id": "FIN-001",
        "name": "Finance Analyst Agent",
        "department": "Finance",
        "purpose": "Financial reporting, invoice analysis, and budgetary variance forecasting",
        "allowed_resources": ["finance_db", "invoice_api", "reporting_api", "budget_sheets"],
        "restricted_resources": ["hr_db", "hr_salary_db", "customer_pii", "prod_infrastructure"],
        "external_access": "restricted",
        "base_risk_level": "MEDIUM",
        "is_active": True
    },
    {
        "id": "DEV-003",
        "name": "Code Maintenance Agent",
        "department": "Engineering",
        "purpose": "Analyze git issues, generate regression patches, and verify CI tests",
        "allowed_resources": ["git_repository", "ci_cd_testing", "issue_tracker", "staging_cluster"],
        "restricted_resources": ["payroll_db", "customer_database", "prod_secrets"],
        "external_access": "restricted",
        "base_risk_level": "LOW",
        "is_active": True
    },
    {
        "id": "SUP-007",
        "name": "Customer Support Agent",
        "department": "Support",
        "purpose": "Answer customer questions, lookup order status, and provide product documentation",
        "allowed_resources": ["knowledge_base", "ticket_system", "order_status_api"],
        "restricted_resources": ["customer_credit_cards", "auth_tokens", "hr_salary_db", "production_db"],
        "external_access": "blocked",
        "base_risk_level": "LOW",
        "is_active": True
    }
]


def seed_default_agents(db: Session):
    """Ensures standard enterprise demo agents are present."""
    for agent_data in DEFAULT_AGENTS:
        existing = db.query(AgentModel).filter(AgentModel.id == agent_data["id"]).first()
        if not existing:
            agent = AgentModel(**agent_data)
            db.add(agent)
    db.commit()


@agents_router.get("", response_model=List[AgentRead])
def list_agents(db: Session = Depends(get_db)):
    """Lists all registered enterprise AI agents."""
    seed_default_agents(db)
    agents = db.query(AgentModel).all()
    return [a.to_dict() for a in agents]


@agents_router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Gets detailed identity and permission profile of a specific agent."""
    seed_default_agents(db)
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent.to_dict()


@agents_router.post("", response_model=AgentRead)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    """Registers a new autonomous AI agent with identity and permission boundaries."""
    existing = db.query(AgentModel).filter(AgentModel.id == agent_in.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent ID already exists")

    agent = AgentModel(**agent_in.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent.to_dict()
