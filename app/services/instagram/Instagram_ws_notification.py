import json
import time
import logging
from typing import Set
from datetime import datetime
from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse

from app.Schemas.instagram.negotiation_schema import SenderType
from app.agents.Instagram.invoke.instagram_agent import instagram_negotiation_agent
from app.config import config
from app.model.Instagram.instagram_message import InstagramMessageModel
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

# -------------------------
# Message deduplication cache
# -------------------------
PROCESSED_MESSAGES: Set[str] = set()
PROCESSED_TTL = 3600  # 1 hour


def cleanup_processed_messages(now: float):
    """Clear processed message cache periodically."""
    if not hasattr(cleanup_processed_messages, "last_run"):
        cleanup_processed_messages.last_run = now
        return

    if now - cleanup_processed_messages.last_run > PROCESSED_TTL:
        PROCESSED_MESSAGES.clear()
        cleanup_processed_messages.last_run = now
        logger.info("Processed message cache cleared")


# -------------------------
# Helpers
# -------------------------
def build_attachments(attachments: list) -> list:
    """Normalize attachments from webhook payload."""
    return [
        {
            "type": att.get("type"),
            "url": att.get("payload", {}).get("url"),
        }
        for att in attachments or []
    ]


IG_BUSINESS_ID = "17841477392364619"


def get_role(sender_id: str) -> str:
    """Determine if sender is AI/admin or user."""
    if sender_id == IG_BUSINESS_ID:
        return SenderType.AI.value
    return SenderType.USER.value


def message_payload(
    *,
    psid: str | None,
    text: str,
    attachments: list,
) -> dict:
    """Normalize message into standard payload."""
    return {
        "thread_id": psid,
        "sender_type": get_role(psid),
        "message": text if text else "[Attachment]",
        "timestamp": datetime.utcnow(),
        "attachments": build_attachments(attachments),
    }


# -------------------------
# Webhook verification
# -------------------------
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == config.META_VERIFY_TOKEN
    ):
        return Response(content=params.get("hub.challenge"), status_code=200)
    return Response(status_code=403)


# -------------------------
# Webhook handler
# -------------------------
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """Main Instagram webhook receiver."""
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    now = time.time()
    cleanup_processed_messages(now)

    for entry in body.get("entry", []):
        # Messenger payload
        for messaging_event in entry.get("messaging", []):
            await process_message_event(messaging_event, background_tasks)

        # Instagram Graph webhook payload
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messaging_event = {
                "message": value.get("message"),
                "sender": value.get("from"),
            }
            await process_message_event(messaging_event, background_tasks)

    return JSONResponse({"status": "received"})


async def process_message_event(
    messaging_event: dict, background_tasks: BackgroundTasks
):
    """Process a single message event."""
    message = messaging_event.get("message")
    if not message:
        return

    message_id = message.get("mid")
    if not message_id or message_id in PROCESSED_MESSAGES:
        return

    PROCESSED_MESSAGES.add(message_id)

    psid = messaging_event.get("sender", {}).get("id")
    payload = message_payload(
        psid=psid,
        text=message.get("text", ""),
        attachments=message.get("attachments", []),
    )

    # Store and broadcast
    await store_and_broadcast(payload, background_tasks)


# -------------------------
# Store message + broadcast + AI agent
# -------------------------
async def store_and_broadcast(payload: dict, background_tasks: BackgroundTasks):
    """
    Store incoming message, broadcast to WS, and invoke AI negotiation.
    """
    try:
        # 1️⃣ Store in DB
        result = await InstagramMessageModel.create(payload)
        payload["id"] = str(result.inserted_id)

        # 2️⃣ Broadcast user message to WS
        ws_manager.broadcast_event("instagram.message", payload=payload)
        background_tasks.add_task(
            ws_manager.broadcast_event, "instagram.message", payload=payload
        )

        # 3️⃣ Only run AI agent for user messages
        if payload["sender_type"] == SenderType.USER:
            background_tasks.add_task(instagram_negotiation_agent, payload)

    except Exception as e:
        logger.exception("Failed to store or process message: %s", e)
