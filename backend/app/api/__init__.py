"""Aggregate and export all API routers."""

from fastapi import APIRouter
from app.api.intercept import intercept_router
from app.api.agents import agents_router
from app.api.policies import policies_router
from app.api.incidents import incidents_router
from app.api.telemetry import telemetry_router
from app.api.simulation import simulation_router
from app.api.websocket import ws_router

api_router = APIRouter()
api_router.include_router(intercept_router)
api_router.include_router(agents_router)
api_router.include_router(policies_router)
api_router.include_router(incidents_router)
api_router.include_router(telemetry_router)
api_router.include_router(simulation_router)

__all__ = ["api_router", "ws_router"]
