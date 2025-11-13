from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional, Dict, Any
from app.core.auth import get_current_user_from_token
from app.services.websocket_manager import ws_manager

router = APIRouter(tags=["WebSockets"])


@router.websocket("/general-ws")
async def websocket_root(websocket: WebSocket, token: Optional[str] = Query(None)):
    """General websocket endpoint.

    Authentication:
        - Provide JWT as query param `token` OR as `Authorization: Bearer <jwt>` header.
    Messages:
        - Incoming JSON will be echoed back with `{type: 'echo'}` wrapper.
        - Special message `{"action": "stats"}` returns connection stats.
    """
    # Attempt token retrieval from header if not query param
    if token is None:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    user: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    if token:
        try:
            user = get_current_user_from_token(token)
            user_id = user.get("user_id")
            role = user.get("role")
        except Exception:
            pass

    await ws_manager.connect(websocket, user_id, role)

    try:
        while True:
            data = await websocket.receive_json()
            if isinstance(data, dict) and data.get("action") == "stats":
                await websocket.send_json(
                    {"type": "stats", **(await ws_manager.stats())}
                )
                continue
            # Echo
            await websocket.send_json({"type": "echo", "received": data})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id, role)
    except Exception as e:
        # Unexpected error - attempt graceful close
        await ws_manager.disconnect(websocket, user_id, role)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket, token: Optional[str] = Query(None)
):
    """Dedicated notifications channel.

    Server pushes only. Clients typically just connect & wait.
    You can still send `{action: 'stats'}` to query stats.
    """
    if token is None:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]

    user_id = None
    role = None
    if token:
        try:
            user = get_current_user_from_token(token)
            user_id = user.get("user_id")
            role = user.get("role")
        except Exception:
            pass

    await ws_manager.connect(websocket, user_id, role)
    try:
        while True:
            data = await websocket.receive_json()
            if isinstance(data, dict) and data.get("action") == "stats":
                await websocket.send_json(
                    {"type": "stats", **(await ws_manager.stats())}
                )
                continue
            # Ignore other incoming messages (could extend later)
            await websocket.send_json({"type": "noop"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id, role)
    except Exception:
        await ws_manager.disconnect(websocket, user_id, role)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
