from __future__ import annotations
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        self._role_connections: Dict[str, Set[WebSocket]] = {}
        self._all_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(
        self, websocket: WebSocket, user_id: Optional[str], role: Optional[str]
    ) -> None:
        await websocket.accept()
        async with self._lock:

            self._all_connections.add(websocket)
            if user_id:
                self._user_connections.setdefault(user_id, set()).add(websocket)
            if role:
                self._role_connections.setdefault(role, set()).add(websocket)

    async def disconnect(
        self, websocket: WebSocket, user_id: Optional[str], role: Optional[str]
    ) -> None:
        async with self._lock:
            self._all_connections.discard(websocket)
            if user_id and user_id in self._user_connections:
                self._user_connections[user_id].discard(websocket)
                if not self._user_connections[user_id]:
                    del self._user_connections[user_id]
            if role and role in self._role_connections:
                self._role_connections[role].discard(websocket)
                if not self._role_connections[role]:
                    del self._role_connections[role]

    async def send_to_user(self, user_id: str, message: Any) -> int:
        """Send message to all sockets of a user. Returns count delivered."""
        async with self._lock:
            sockets = list(self._user_connections.get(user_id, []))
        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception:
                pass
        return delivered

    async def broadcast(self, message: Any) -> int:
        async with self._lock:
            sockets = list(self._all_connections)
        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception:
                pass
        return delivered

    async def broadcast_role(self, role: str, message: Any) -> int:
        async with self._lock:
            sockets = list(self._role_connections.get(role, []))
        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception:
                pass
        return delivered

    async def stats(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "users": len(self._user_connections),
                "authenticated_connections": sum(
                    len(s) for s in self._user_connections.values()
                ),
                "total_connections": len(self._all_connections),
                "roles": {r: len(s) for r, s in self._role_connections.items()},
            }


ws_manager = WebSocketManager()
