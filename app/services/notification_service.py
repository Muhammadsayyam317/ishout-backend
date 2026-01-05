from typing import Any, Dict
from fastapi import WebSocket, WebSocketDisconnect, status
from app.core.security.jwt import verify_token
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
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = verify_token(token)
    if payload.get("role") != "admin":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["user_id"]
    await ws_manager.connect(websocket, user_id=user_id, role="admin")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id=user_id, role="admin")
