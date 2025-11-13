"""Notification service leveraging the WebSocketManager.

Provides simple functions to push real-time notifications to users or roles.
Extend with persistence (e.g., Mongo collection) if you need offline storage.
"""

from typing import Any, Dict
from .websocket_manager import ws_manager


async def send_notification(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    delivered = await ws_manager.send_to_user(user_id, {"type": "notification", **payload})
    return {"delivered": delivered}


async def broadcast_notification(payload: Dict[str, Any]) -> Dict[str, Any]:
    delivered = await ws_manager.broadcast({"type": "notification", **payload})
    return {"delivered": delivered}


async def broadcast_to_role(role: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    delivered = await ws_manager.broadcast_role(role, {"type": "notification", **payload})
    return {"delivered": delivered}
