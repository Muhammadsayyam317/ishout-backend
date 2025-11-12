import os
import json
import hmac
import hashlib
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException, Request, BackgroundTasks
from fastapi import status
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from app.services.notification_service import broadcast_to_role

# --- Config via env -----------------------------------------------------------
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "replace-me")
APP_SECRET   = os.getenv("META_APP_SECRET", "replace-me")
PAGE_TOKEN   = os.getenv("PAGE_ACCESS_TOKEN", "replace-me")
GRAPH_VER    = os.getenv("IG_GRAPH_API_VERSION", "v23.0")

GRAPH_SEND_URL = f"https://graph.facebook.com/{GRAPH_VER}/me/messages"

# --- In-memory demo stores (swap with your DB layer) --------------------------
CONVERSATIONS = {}  # key: (ig_page_id, user_psid) -> metadata
MESSAGES = []       # append-only event log


# --- Helpers ------------------------------------------------------------------
def _compute_signature(raw_body: bytes) -> str:
    digest = hmac.new(APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"

def _verify_signature(request_signature: Optional[str], raw_body: bytes) -> None:
    if not APP_SECRET or APP_SECRET == "replace-me":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "App secret not configured")
    if not request_signature:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-Hub-Signature-256")

    expected = _compute_signature(raw_body)
    if not hmac.compare_digest(request_signature, expected):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature")

def _extract_events(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for entry in payload.get("entry", []):
        entry_id = entry.get("id")

        if isinstance(entry.get("messaging"), list):
            for ev in entry["messaging"]:
                ev["_entry_id"] = entry_id
                events.append(ev)

        for change in entry.get("changes", []):
            value = change.get("value") or {}
            msgs = value.get("messages") or value.get("messaging") or []
            for ev in msgs:
                ev["_entry_id"] = entry_id or value.get("id")
                events.append(ev)
    return events

def _upsert_conversation(ig_page_id: str, psid: str) -> Tuple[str, str]:
    key = (ig_page_id, psid)
    if key not in CONVERSATIONS:
        CONVERSATIONS[key] = {"ig_page_id": ig_page_id, "psid": psid, "last_event_ts": None}
    return key

async def _handle_message_event_async(ev: Dict[str, Any]) -> None:
    sender = ev.get("sender", {}).get("id")
    recipient = ev.get("recipient", {}).get("id")
    timestamp = ev.get("timestamp")
    message   = ev.get("message")
    reaction  = ev.get("reaction")
    delivery  = ev.get("delivery")
    read      = ev.get("read")

    ig_page_id = recipient or ev.get("_entry_id") or "unknown"
    user_psid  = sender or "unknown"

    key = _upsert_conversation(ig_page_id, user_psid)
    CONVERSATIONS[key]["last_event_ts"] = timestamp

    MESSAGES.append({
        "ig_page_id": ig_page_id,
        "user_psid": user_psid,
        "timestamp": timestamp,
        "type": (
            "message" if message else
            "reaction" if reaction else
            "delivery" if delivery else
            "read" if read else
            "other"
        ),
        "payload": ev,
    })

    # Minimal MVP: when a message arrives (user -> admin), broadcast a realtime notification
    if message and message.get("text"):
        await broadcast_to_role("admin", {
            "type": "ig_reply",
            "from_psid": user_psid,
            "to_page_id": ig_page_id,
            "text": message.get("text"),
            "timestamp": timestamp,
        })


# --- Webhook entry (GET verify + POST deliver) --------------------------------
async def webhook(request: Request, background: Optional[BackgroundTasks] = None):
    if request.method == "GET":
        mode           = request.query_params.get("hub.mode")
        hub_challenge  = request.query_params.get("hub.challenge")
        hub_verify_tok = request.query_params.get("hub.verify_token")

        if mode == "subscribe" and hub_challenge and hub_verify_tok == VERIFY_TOKEN:
            return PlainTextResponse(content=hub_challenge, status_code=status.HTTP_200_OK)
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Verification failed")

    if request.method == "POST":
        raw_body = await request.body()
        _verify_signature(request.headers.get("X-Hub-Signature-256"), raw_body)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid JSON")

        events = _extract_events(payload)

        if background:
            # Schedule async tasks for each event
            for ev in events:
                background.add_task(_handle_message_event_async, ev)
        else:
            for ev in events:
                await _handle_message_event_async(ev)

        return JSONResponse(status_code=200, content={"status": "ok", "received": len(events)})

    return JSONResponse(status_code=405, content={"message": "Method not allowed"})


# --- Debug: inspect state -----------------------------------------------------
class StateResponse(BaseModel):
    conversations: int
    messages: int
    sample_conversations: List[Dict[str, Any]]
    sample_messages: List[Dict[str, Any]]

async def debug_state(limit: int = 5):
    conv_list = [
        {"ig_page_id": ig, "psid": psid, **meta}
        for ((ig, psid), meta) in list(CONVERSATIONS.items())[:limit]
    ]
    sample_msgs = MESSAGES[-limit:]
    return StateResponse(
        conversations=len(CONVERSATIONS),
        messages=len(MESSAGES),
        sample_conversations=conv_list,
        sample_messages=sample_msgs,
    )


# --- Send API: DM endpoint ----------------------------------------------------
class DMRequest(BaseModel):
    psid: Optional[str] = Field(default=None, description="Recipient PSID. If omitted, uses the most recent sender.")
    text: str

async def send_dm(body: DMRequest):
    # Choose recipient: given PSID or the last one we saw via webhook
    recipient_psid = body.psid
    if not recipient_psid:
        if not MESSAGES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No recent PSID seen; provide 'psid'.")
        recipient_psid = MESSAGES[-1]["user_psid"]

    if not PAGE_TOKEN or PAGE_TOKEN == "replace-me":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "PAGE_ACCESS_TOKEN not configured")

    payload = {
        "messaging_product": "instagram",
        "recipient": {"id": recipient_psid},
        "message": {"text": body.text},
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            GRAPH_SEND_URL,
            params={"access_token": PAGE_TOKEN},
            json=payload,
        )
        if resp.status_code >= 300:
            # Bubble up Graph error detail for easier debugging
            try:
                detail = resp.json()
            except Exception:
                detail = {"text": await resp.aread()}
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail)

    return {"status": "sent", "recipient_psid": recipient_psid}


# --- Local-only mock webhook (no signature) -----------------------------------
class MockEvent(BaseModel):
    sender_psid: str = "TEST_USER_PSID"
    recipient_id: str = "TEST_PAGE_ID"
    text: Optional[str] = "ping"

async def mock_webhook(ev: MockEvent):
    # Simulate a minimal message event shape
    simulated = {
        "entry": [{
            "id": ev.recipient_id,
            "messaging": [{
                "sender": {"id": ev.sender_psid},
                "recipient": {"id": ev.recipient_id},
                "timestamp": 0,
                "message": {"mid": "mid.mock", "text": ev.text},
            }]
        }]
    }
    for e in _extract_events(simulated):
        await _handle_message_event_async(e)
    return {"status": "mocked", "psid": ev.sender_psid}
