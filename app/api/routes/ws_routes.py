from typing import Optional
from fastapi import (
    APIRouter,
    Request,
    BackgroundTasks,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from app.services.websocket_manager import ws_manager
from app.config import config

router = APIRouter()


@router.get("/meta")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    print("🔍 Meta verification params:", params)

    mode = params.get("hub.mode") == "subscribe"
    token = params.get("hub.verify_token") == config.META_VERIFY_TOKEN
    challenge = params.get("hub.challenge")

    if mode and token and challenge:
        print("Webhook verified successfully.")
        return Response(content=challenge, status_code=200)

    print("Webhook verification failed.")
    return Response(status_code=403)


@router.post("/meta")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print("Incoming webhook:", body)

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "message" in value:
                await ws_manager.broadcast(
                    {
                        "type": "ig_reply",
                        "from_psid": value.get("from", {}).get("id"),
                        "to_page_id": value.get("to", {}).get("id"),
                        "from_username": value.get("from", {}).get(
                            "username",
                        ),
                        "text": value["message"].get("text", ""),
                        "timestamp": value.get("timestamp"),
                    }
                )

    return JSONResponse({"status": "received"})


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket, token: Optional[str] = None):
    """
    Admin clients connect here to receive live Instagram messages
    """
    await ws_manager.connect(websocket, user_id=None, role="admin")
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
        await ws_manager.disconnect(websocket, user_id=None, role="admin")
    except Exception:
        await ws_manager.disconnect(websocket, user_id=None, role="admin")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
