"""Universal One-Command Launcher for AgentGuard Live."""


import sys
import os
from pathlib import Path

# Add backend directory to Python sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import uvicorn
    from app.config import HOST, PORT, DEBUG
except ImportError as e:
    print(f"[Error] Required packages not found: {e}")
    print("Please run: pip install -r backend/requirements.txt")
    sys.exit(1)


def print_banner():
    banner = f"""
    ======================================================================
       [+] AGENTGUARD LIVE -- AI Agent Security & Governance Platform
    ======================================================================
       Control Plane:    http://{HOST}:{PORT}
       Live Dashboard:   http://{HOST}:{PORT}
       Swagger API Docs: http://{HOST}:{PORT}/docs
       WebSocket Stream: ws://{HOST}:{PORT}/ws/live
    ======================================================================
       Ready for Live Demonstration! Press Ctrl+C to terminate.
    ======================================================================
    """
    print(banner)


def main():
    print_banner()
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,  # False for stable demonstration runs
        log_level="info"
    )


if __name__ == "__main__":
    main()
