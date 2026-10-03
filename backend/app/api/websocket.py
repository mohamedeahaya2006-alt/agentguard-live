"""WebSocket Connection Manager and Real-Time Event Broadcaster."""

import json
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections to dashboard clients."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcasts a JSON message to all connected clients."""
        dead_connections = []
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


manager = ConnectionManager()


@ws_router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time bi-directional streaming endpoint for the dashboard."""
    await manager.connect(websocket)
    try:
        # Send initial handshake
        await websocket.send_text(json.dumps({
            "type": "SYSTEM_STATUS",
            "data": {"status": "ONLINE", "message": "AgentGuard Live Control Plane connected"}
        }))
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            # Optional echo / ping
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "PONG"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
