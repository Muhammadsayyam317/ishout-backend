"""WebSocket connection manager for real-time features.

Supports:
- Tracking active connections per user
- Broadcasting to all users
- Sending personal messages
- Broadcasting to roles (admin/company) if role info supplied

Design notes:
We keep an in-memory registry. For production horizontal scaling you'd
introduce a pub/sub layer (Redis, NATS, etc.). This implementation is
intentionally minimal and synchronous except for send operations.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        # user_id -> set of websockets (support multi-tab)
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        # role -> set of websockets
        self._role_connections: Dict[str, Set[WebSocket]] = {}
        # all connected websockets (including anonymous)
        self._all_connections: Set[WebSocket] = set()
        # lock for mutation
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: Optional[str], role: Optional[str]) -> None:
        await websocket.accept()
        async with self._lock:
            # Always track all connections
            self._all_connections.add(websocket)
            if user_id:
                self._user_connections.setdefault(user_id, set()).add(websocket)
            if role:
                self._role_connections.setdefault(role, set()).add(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: Optional[str], role: Optional[str]) -> None:
        async with self._lock:
            # Remove from all connections
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
                # Silently ignore; cleanup happens on next disconnect or per-call if desired
                pass
        return delivered

    async def broadcast(self, message: Any) -> int:
        """Broadcast to all connected sockets (across all users, including anonymous)."""
        async with self._lock:
            # Use all connections including anonymous
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
                "authenticated_connections": sum(len(s) for s in self._user_connections.values()),
                "total_connections": len(self._all_connections),
                "roles": {r: len(s) for r, s in self._role_connections.items()},
            }


# Singleton instance used across the app
ws_manager = WebSocketManager()
