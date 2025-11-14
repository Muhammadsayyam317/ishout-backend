import json
import time
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    status,
)
from fastapi.responses import JSONResponse
from app.services.websocket_manager import ws_manager
from app.config import config
from app.core.auth import verify_token

router = APIRouter()


async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.META_VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)


async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "message" in value:
                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": value.get("from", {}).get("id"),
                        "to_page_id": value.get("to", {}).get("id"),
                        "from_username": value.get("from", {}).get("username"),
                        "text": value["message"].get("text", ""),
                        "timestamp": value.get("timestamp", time.time()),
                    },
                )

    return JSONResponse({"status": "received"})


async def websocket_notifications(websocket: WebSocket):
    # Get token from query parameters
    token = websocket.query_params.get("token")

    if not token:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Missing token"
        )
        return

    # Verify token before accepting connection
    user_id = None
    role = None
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")

        # Only allow admin users
        if role != "admin":
            await websocket.accept()
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Admin access required"
            )
            return
    except HTTPException as e:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=e.detail)
        return
    except Exception:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token"
        )
        return

    # Token is valid, connect (this will accept the connection)
    await ws_manager.connect(websocket, user_id=user_id, role=role)
    try:
        while True:
            data = await websocket.receive_json()
            if isinstance(data, dict) and data.get("action") == "stats":
                await websocket.send_json(
                    {"type": "stats", **(await ws_manager.stats())}
                )
            else:
                await websocket.send_json({"type": "noop"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id=user_id, role=role)
    except Exception:
        await ws_manager.disconnect(websocket, user_id=user_id, role=role)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
