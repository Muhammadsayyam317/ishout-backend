from typing import Optional
from fastapi import (
    APIRouter,
    Request,
    BackgroundTasks,
    WebSocket,
    WebSocketDisconnect,
    Query,
    Response,
)
from app.core.auth import get_current_user_from_token
from app.services.websocket_manager import ws_manager

router = APIRouter()
VERIFY_TOKEN = "longrandomstring123"  # Must match Meta dashboard


@router.get("/meta")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    print("🔍 Meta verification params:", params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print(" Meta Webhook verified successfully.")
        return Response(content=challenge, status_code=200)

    print(" Meta Webhook verification failed.")
    return Response(status_code=403)


@router.post("/meta")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print(" Incoming Meta Webhook POST:", body)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "message" in value:
                await ws_manager.broadcast(
                    {
                        "type": "ig_reply",
                        "from_username": value.get("from", {}).get(
                            "username", "unknown"
                        ),
                        "text": value["message"].get("text", ""),
                        "timestamp": value.get("timestamp"),
                    }
                )
    return {"status": "received"}


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
            await websocket.send_json({"type": "noop"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, user_id, role)
    except Exception:
        await ws_manager.disconnect(websocket, user_id, role)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
