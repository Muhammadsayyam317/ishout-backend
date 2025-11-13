import json
import hmac
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse, PlainTextResponse
from app.services.websocket_manager import ws_manager
from app.config import config

VERIFY_TOKEN: str = config.META_VERIFY_TOKEN
APP_SECRET: str = config.META_APP_SECRET
PAGE_TOKEN: str = config.PAGE_ACCESS_TOKEN
GRAPH_VER: str = config.IG_GRAPH_API_VERSION

GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_VER}"
GRAPH_SEND_URL = f"{GRAPH_BASE_URL}/me/messages"

CONVERSATIONS: Dict[Tuple[str, str], Dict[str, Any]] = {}
MESSAGES: List[Dict[str, Any]] = []
PROFILE_CACHE: Dict[str, Dict[str, Any]] = {}
PROFILE_TTL_SEC = 3600


# === Utility Functions ===
def _compute_signature(raw_body: bytes) -> str:
    """Compute HMAC SHA-256 signature for webhook body."""
    digest = hmac.new(APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _verify_signature(signature: Optional[str], raw_body: bytes) -> None:
    """Verify webhook request signature."""
    if not APP_SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "App secret not configured")

    if not signature:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Missing X-Hub-Signature-256 header"
        )

    expected_sig = _compute_signature(raw_body)
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")


def _extract_events(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract individual messaging events from the Meta payload."""
    events = []
    for entry in payload.get("entry", []):
        entry_id = entry.get("id")
        for msg in entry.get("messaging", []) or []:
            msg["_entry_id"] = entry_id
            events.append(msg)

        # Handle IG messaging changes
        for change in entry.get("changes", []) or []:
            value = change.get("value", {})
            msgs = value.get("messages") or value.get("messaging") or []
            for ev in msgs:
                ev["_entry_id"] = entry_id or value.get("id")
                events.append(ev)
    return events


def _upsert_conversation(ig_page_id: str, psid: str) -> Tuple[str, str]:
    key = (ig_page_id, psid)
    if key not in CONVERSATIONS:
        CONVERSATIONS[key] = {
            "ig_page_id": ig_page_id,
            "psid": psid,
            "last_event_ts": None,
        }
    return key


# === Event Handlers ===
async def _handle_message_event(ev: Dict[str, Any]) -> None:
    """Handle a single incoming message event."""
    sender = ev.get("sender", {}).get("id")
    recipient = ev.get("recipient", {}).get("id")
    timestamp = ev.get("timestamp")
    message = ev.get("message")
    reaction = ev.get("reaction")
    delivery = ev.get("delivery")
    read = ev.get("read")

    ig_page_id = recipient or ev.get("_entry_id") or "unknown"
    user_psid = sender or "unknown"

    key = _upsert_conversation(ig_page_id, user_psid)
    CONVERSATIONS[key]["last_event_ts"] = timestamp

    event_type = (
        "message"
        if message
        else (
            "reaction"
            if reaction
            else "delivery" if delivery else "read" if read else "other"
        )
    )

    MESSAGES.append(
        {
            "ig_page_id": ig_page_id,
            "user_psid": user_psid,
            "timestamp": timestamp,
            "type": event_type,
            "payload": ev,
        }
    )

    from_username = await _get_ig_sender_username(user_psid)
    if message and message.get("text"):
        await ws_manager.broadcast(
            {
                "type": "ig_reply",
                "from_psid": user_psid,
                "to_page_id": ig_page_id,
                "text": message["text"],
                "timestamp": timestamp,
                "from_username": from_username,
            }
        )


# === Webhook Endpoint ===
async def webhook(request: Request, background: Optional[BackgroundTasks] = None):
    """Main Meta webhook endpoint."""
    # GET — verification
    if request.method == "GET":
        mode = request.query_params.get("hub.mode")
        challenge = request.query_params.get("hub.challenge")
        token = request.query_params.get("hub.verify_token")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return PlainTextResponse(challenge)
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Verification failed")

    # POST — events
    if request.method == "POST":
        raw_body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        client_ip = request.client.host if request.client else "unknown"

        print(
            f"📥 Webhook from {client_ip} | {len(raw_body)} bytes | Signature: {'present' if signature else 'missing'}"
        )

        # Verify signature
        try:
            _verify_signature(signature, raw_body)
        except HTTPException as e:
            print(f"❌ Invalid signature: {e.detail}")
            raise

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON body")

        events = _extract_events(payload)
        print(f"✅ Received {len(events)} event(s)")

        if background:
            for ev in events:
                background.add_task(_handle_message_event, ev)
        else:
            for ev in events:
                await _handle_message_event(ev)

        return JSONResponse({"status": "ok", "received": len(events)})

    return JSONResponse({"message": "Method not allowed"}, status_code=405)


# === IG Username Fetch ===
async def _get_ig_sender_username(psid: Optional[str]) -> Optional[str]:
    if not psid or not PAGE_TOKEN:
        return None

    now = time.time()
    cached = PROFILE_CACHE.get(psid)
    if cached and now - cached["ts"] < PROFILE_TTL_SEC:
        return cached.get("username") or cached.get("name")

    url = f"{GRAPH_BASE_URL}/{psid}"
    params = {"fields": "username,name", "access_token": PAGE_TOKEN}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                PROFILE_CACHE[psid] = {
                    "username": data.get("username"),
                    "name": data.get("name"),
                    "ts": now,
                }
                return data.get("username") or data.get("name")
    except Exception:
        pass
    return None
