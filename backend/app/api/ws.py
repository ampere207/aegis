from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import logging
from typing import Dict, List
import json

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, repo_id: int):
        await websocket.accept()
        if repo_id not in self.active_connections:
            self.active_connections[repo_id] = []
        self.active_connections[repo_id].append(websocket)

    def disconnect(self, websocket: WebSocket, repo_id: int):
        if repo_id in self.active_connections:
            self.active_connections[repo_id].remove(websocket)

    async def broadcast(self, repo_id: int, message: dict):
        if repo_id in self.active_connections:
            for connection in self.active_connections[repo_id]:
                await connection.send_text(json.dumps(message))

manager = ConnectionManager()

@router.websocket("/ws/analysis/{repo_id}")
async def analysis_websocket(websocket: WebSocket, repo_id: int):
    await manager.connect(websocket, repo_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, repo_id)
