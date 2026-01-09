from __future__ import annotations
import asyncio
from typing import Dict, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self._all_connections: Set[WebSocket] = set()
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        self._role_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        *,
        user_id: str | None = None,
        role: str | None = None,
    ):
        await websocket.accept()
        async with self._lock:
            self._all_connections.add(websocket)

            if user_id:
                self._user_connections.setdefault(user_id, set()).add(websocket)
            if role:
                self._role_connections.setdefault(role, set()).add(websocket)
        print(f"🔌 WS connected | total={len(self._all_connections)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self._all_connections.discard(websocket)

            for sockets in self._user_connections.values():
                sockets.discard(websocket)
            for sockets in self._role_connections.values():
                sockets.discard(websocket)

        print(f"❌ WS disconnected | total={len(self._all_connections)}")

    async def broadcast_event(self, event_type: str, payload: dict) -> int:
        message = {
            "type": event_type,
            "payload": payload,
        }

        async with self._lock:
            sockets = list(self._all_connections)

        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception as e:
                print("WS send failed:", e)

        print(f"📡 Broadcast `{event_type}` → {delivered} clients")
        return delivered

    async def broadcast_role(self, role: str, payload: dict) -> int:
        async with self._lock:
            sockets = list(self._role_connections.get(role, []))

        delivered = 0
        for ws in sockets:
            try:
                await ws.send_json(payload)
                delivered += 1
            except Exception:
                pass
        return delivered


ws_manager = WebSocketManager()
