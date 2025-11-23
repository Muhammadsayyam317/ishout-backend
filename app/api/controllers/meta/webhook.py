import json
import time
from typing import Optional, Dict
import httpx
from fastapi import BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response
from app.services.websocket_manager import ws_manager
from app.config import config

# Profile cache to avoid repeated API calls
PROFILE_CACHE: Dict[str, Dict] = {}
PROFILE_TTL_SEC = 3600


async def _get_ig_username(psid: Optional[str]) -> Optional[str]:
    """Fetch Instagram username from PSID using Graph API with caching."""
    if not psid or not config.PAGE_ACCESS_TOKEN:
        return None
    now = time.time()
    cached = PROFILE_CACHE.get(psid)
    if cached and now - cached.get("ts", 0) < PROFILE_TTL_SEC:
        return cached.get("username") or cached.get("name")
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
                PROFILE_CACHE[psid] = {
                    "username": data.get("username"),
                    "name": data.get("name"),
                    "ts": now,
                }
                return username
            else:
                print(f"Failed to fetch username for PSID {psid}: {resp.status_code}")
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

        # Handle Facebook Messenger/Instagram format: entry[].messaging[]
        for messaging_event in entry.get("messaging", []):
            message = messaging_event.get("message")
            if message and message.get("text"):
                sender = messaging_event.get("sender", {})
                recipient = messaging_event.get("recipient", {})
                psid = sender.get("id")

                # Fetch username from Graph API
                username = await _get_ig_username(psid)

                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": psid,
                        "to_page_id": recipient.get("id"),
                        "from_username": username,
                        "text": message.get("text", ""),
                        "timestamp": messaging_event.get("timestamp", time.time()),
                    },
                )

    return JSONResponse({"status": "received"})
