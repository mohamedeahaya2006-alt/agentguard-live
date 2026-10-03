"""Configuration settings and risk scoring weights for AgentGuard Live."""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR.parent / "frontend" / "static"

# Server Settings
HOST = os.getenv("AGENTGUARD_HOST", "127.0.0.1")
PORT = int(os.getenv("AGENTGUARD_PORT", "8000"))
DEBUG = os.getenv("AGENTGUARD_DEBUG", "True").lower() in ("true", "1")

# Database Settings (SQLite local file by default, postgresql compatible)
DB_PATH = BASE_DIR / "agentguard.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Risk Scoring Weights (Must sum to 1.0)
WEIGHT_PERMISSION = 0.25
WEIGHT_DATA_SENSITIVITY = 0.20
WEIGHT_GOAL_MISMATCH = 0.20
WEIGHT_BEHAVIORAL_ANOMALY = 0.15
WEIGHT_DESTINATION = 0.10
WEIGHT_POLICY = 0.10

# Decision Boundaries
THRESHOLD_ALLOW_MAX = 30.0   # Scores < 30 -> ALLOW (Green)
THRESHOLD_WARN_MAX = 70.0    # Scores 30..70 -> WARN/PAUSE (Yellow)
                             # Scores >= 70 -> BLOCK (Red)

# LLM & AI Engine Configuration
# Supported providers: "gemini", "openai", "offline_heuristic"
AI_PROVIDER = os.getenv("AI_PROVIDER", "offline_heuristic")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
