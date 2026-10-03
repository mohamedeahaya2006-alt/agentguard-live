"""Main FastAPI Application Entry Point for AgentGuard Live."""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import STATIC_DIR, DEBUG
from app.database import engine, Base, SessionLocal
from app.api import api_router, ws_router
from app.api.agents import seed_default_agents
from app.api.policies import seed_default_policies


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    # Create DB tables
    Base.metadata.create_all(bind=engine)
    # Seed default enterprise agents and security policies
    db = SessionLocal()
    try:
        seed_default_agents(db)
        seed_default_policies(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AgentGuard Live",
    description="Real-Time AI Agent Security, Risk & Governance Platform",
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket routes
app.include_router(api_router)
app.include_router(ws_router)

# Mount frontend static directory if exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"status": "online", "message": "AgentGuard Live API is running. Frontend static files pending."}
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "title": "AgentGuard Live",
            "tagline": "Real-Time AI Agent Security, Risk & Governance Platform",
            "status": "ONLINE",
            "docs": "/docs",
            "api": "/api/v1"
        }
