from typing import Any, Dict
from fastapi import WebSocket
from .websocket_manager import ws_manager


async def send_notification(user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    delivered = await ws_manager.send_to_user(
        user_id, {"type": "notification", **payload}
    )
    return {"delivered": delivered}


async def broadcast_notification(event: str, payload: Dict[str, Any]):
    return await ws_manager.broadcast({"type": event, "payload": payload})


async def broadcast_to_role(role: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    delivered = await ws_manager.broadcast_role(
        role, {"type": "notification", **payload}
    )
    return {"delivered": delivered}


async def admin_ws(websocket: WebSocket):
    await ws_manager.connect(
        websocket,
        role="ADMIN",
    )
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        await ws_manager.disconnect(websocket)
