import json
import time
from typing import Optional, Dict
import httpx
from fastapi import (
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

# Profile cache to avoid repeated API calls
PROFILE_CACHE: Dict[str, Dict] = {}
PROFILE_TTL_SEC = 3600  # Cache for 1 hour
PROCESSED_MESSAGES: set = set()
MESSAGE_CACHE_TTL_SEC = 3600


async def _get_ig_user(psid: str, page_id: str):
    """Fetch Instagram user info (username + profile pic) via Conversations API only."""

    if not psid or not page_id:
        return None

    url = f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/{page_id}/conversations"

    params = {
        "fields": "participants{id,username,name}",
        "access_token": config.PAGE_ACCESS_TOKEN,
        "limit": 25,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)

            if resp.status_code != 200:
                print(f"Conversations API error {resp.status_code}")
                return None

            data = resp.json()

            for conv in data.get("data", []):
                participants = conv.get("participants", {}).get("data", [])

                for p in participants:
                    if p.get("id") == psid:
                        username = p.get("username") or p.get("name")

                        print(f"Username: {username}")

                        return username

    except Exception as e:
        print(f"⚠️ Username fetch failed: {str(e)}")

    return None


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
        print(" Invalid JSON received")
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    print("📩 Incoming Webhook Body:", json.dumps(body, indent=2))
    current_time = time.time()
    if hasattr(handle_webhook, "_last_cleanup"):
        if current_time - handle_webhook._last_cleanup > 3600:
            PROCESSED_MESSAGES.clear()
            handle_webhook._last_cleanup = current_time
    else:
        handle_webhook._last_cleanup = current_time

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            if "message" in value:
                message_id = value["message"].get("mid")
                if message_id and message_id in PROCESSED_MESSAGES:
                    print(f"Skipping duplicate message: {message_id}")
                    continue

                if message_id:
                    PROCESSED_MESSAGES.add(message_id)

                username = await _get_ig_user(
                    value.get("from", {}).get("id"), value.get("to", {}).get("id")
                )
                psid = value.get("from", {}).get("id")
                text = value["message"].get("text", "")

                print("=========== IG MESSAGE RECEIVED (Direct) ===========")
                print(f" Username: {username}")
                print(f" PSID: {psid}")
                print(f" Message: {text}")
                print("===========================================")

                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": psid,
                        "to_page_id": value.get("to", {}).get("id"),
                        "from_username": username["username"],
                        "from_profile_pic_url": username["profile_pic_url"],
                        "text": text,
                        "timestamp": value.get("timestamp", time.time()),
                    },
                )
    return JSONResponse({"status": "received"})


async def websocket_notifications(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="Missing token"
        )
        return
    user_id = None
    role = None
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")
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
