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

# Message deduplication to prevent processing same message twice
PROCESSED_MESSAGES: set = set()
MESSAGE_CACHE_TTL_SEC = 3600  # Keep message IDs for 1 hour


async def _get_ig_username(
    psid: Optional[str], page_id: Optional[str] = None
) -> Optional[str]:
    """Fetch Instagram username from PSID using Graph API with caching."""
    if not psid or not config.PAGE_ACCESS_TOKEN:
        return None

    now = time.time()
    cached = PROFILE_CACHE.get(psid)
    if cached and now - cached.get("ts", 0) < PROFILE_TTL_SEC:
        return cached.get("username") or cached.get("name")

    # Method 1: Try direct PSID query (works for Facebook Messenger, may not work for Instagram)
    graph_url = f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/{psid}"
    params = {
        "fields": "username,name",
        "access_token": config.PAGE_ACCESS_TOKEN,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(graph_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                username = data.get("username") or data.get("name")
                if username:
                    PROFILE_CACHE[psid] = {
                        "username": data.get("username"),
                        "name": data.get("name"),
                        "ts": now,
                    }
                    return username
            elif resp.status_code == 403:
                print(
                    f"Direct PSID access denied (403) for {psid} - Instagram API restriction"
                )
                print("💡 Instagram doesn't allow direct user profile queries via PSID")
                print(
                    "💡 Username will show as PSID until user sends a message with username in webhook"
                )
    except Exception as e:
        print(f"Error fetching username for PSID {psid}: {str(e)}")

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

    # Clean old message IDs from cache (older than 1 hour)
    current_time = time.time()
    if hasattr(handle_webhook, "_last_cleanup"):
        if current_time - handle_webhook._last_cleanup > 3600:  # Clean every hour
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
                    print(f"⏭️ Skipping duplicate message: {message_id}")
                    continue

                if message_id:
                    PROCESSED_MESSAGES.add(message_id)

                username = value.get("from", {}).get("username")
                psid = value.get("from", {}).get("id")
                text = value["message"].get("text", "")

                print("=========== IG MESSAGE RECEIVED (Direct) ===========")
                print(f"👤 Username: {username}")
                print(f"🆔 PSID: {psid}")
                print(f"💬 Message: {text}")
                print("===========================================")

                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": psid,
                        "to_page_id": value.get("to", {}).get("id"),
                        "from_username": username,
                        "text": text,
                        "timestamp": value.get("timestamp", time.time()),
                    },
                )

        # Handle Facebook Messenger/Instagram format: entry[].messaging[]
        for messaging_event in entry.get("messaging", []):
            message = messaging_event.get("message")
            if message and message.get("text"):
                message_id = message.get("mid")
                # Skip if message already processed
                if message_id and message_id in PROCESSED_MESSAGES:
                    print(f"⏭️ Skipping duplicate message: {message_id}")
                    continue

                if message_id:
                    PROCESSED_MESSAGES.add(message_id)

                sender = messaging_event.get("sender", {})
                recipient = messaging_event.get("recipient", {})
                psid = sender.get("id")
                page_id = recipient.get("id")
                text = message.get("text", "")
                timestamp = messaging_event.get("timestamp", time.time())
                username = await _get_ig_username(psid, page_id)
                display_name = username or f"User_{psid[:8]}"

                print("=========== IG MESSAGE RECEIVED (Messaging) ===========")
                print(f"👤 Username: {display_name}")
                print(f"🆔 PSID: {psid}")
                print(f"📄 Page ID: {page_id}")
                print(f"💬 Message: {text}")
                print("===========================================")

                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": psid,
                        "to_page_id": page_id,
                        "from_username": display_name,
                        "text": text,
                        "timestamp": timestamp,
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
