import json
import time
from typing import Optional, Dict
import httpx
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

# Profile cache to avoid repeated API calls
PROFILE_CACHE: Dict[str, Dict] = {}
PROFILE_TTL_SEC = 3600  # Cache for 1 hour

router = APIRouter()


async def _get_ig_username(psid: Optional[str]) -> Optional[str]:
    """Fetch Instagram username from PSID using Graph API with caching."""
    if not psid or not config.PAGE_ACCESS_TOKEN:
        return None

    # Check cache first
    now = time.time()
    cached = PROFILE_CACHE.get(psid)
    if cached and now - cached.get("ts", 0) < PROFILE_TTL_SEC:
        return cached.get("username") or cached.get("name")

    # Fetch from Graph API
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
                # Cache the result
                PROFILE_CACHE[psid] = {
                    "username": data.get("username"),
                    "name": data.get("name"),
                    "ts": now,
                }
                return username
            else:
                print(f"⚠️ Failed to fetch username for PSID {psid}: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Error fetching username for PSID {psid}: {str(e)}")

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

    for entry in body.get("entry", []):
        # Handle Instagram Direct format: entry[].changes[].value
        for change in entry.get("changes", []):
            value = change.get("value", {})

            if "message" in value:
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
                sender = messaging_event.get("sender", {})
                recipient = messaging_event.get("recipient", {})
                psid = sender.get("id")
                page_id = recipient.get("id")
                text = message.get("text", "")
                timestamp = messaging_event.get("timestamp", time.time())

                # Fetch username from Graph API
                username = await _get_ig_username(psid)

                print("=========== IG MESSAGE RECEIVED (Messaging) ===========")
                print(f"👤 Username: {username or 'Unknown'}")
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
                        "from_username": username,
                        "text": text,
                        "timestamp": timestamp,
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
