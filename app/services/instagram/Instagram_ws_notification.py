import json
import time
import logging
from typing import Set
from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from app.agents.Instagram.invoke.instagram_agent import instagram_negotiation_agent
from app.config import config
from app.model.Instagram.instagram_message import InstagramMessageModel
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

PROCESSED_MESSAGES: Set[str] = set()
PROCESSED_TTL = 3600  # 1 hour


async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == config.META_VERIFY_TOKEN
    ):
        return Response(content=params.get("hub.challenge"), status_code=200)
    return Response(status_code=403)


# Helpers
def cleanup_processed_messages(now: float):
    if not hasattr(cleanup_processed_messages, "last_run"):
        cleanup_processed_messages.last_run = now
        return

    if now - cleanup_processed_messages.last_run > PROCESSED_TTL:
        PROCESSED_MESSAGES.clear()
        cleanup_processed_messages.last_run = now
        logger.info("Processed message cache cleared")


def build_attachments(attachments: list) -> list:
    return [
        {
            "type": att.get("type"),
            "url": att.get("payload", {}).get("url"),
        }
        for att in attachments or []
    ]


def message_payload(
    *,
    psid: str | None,
    text: str,
    attachments: list,
    timestamp: float,
) -> dict:
    return {
        "thread_id": psid,
        "sender_type": "ADMIN",
        "platform": "INSTAGRAM",
        "username": "Admin",
        "message": text if text else "[Attachment]",
        "timestamp": time.time(),
        "attachments": build_attachments(attachments),
    }


# -------------------------
# Webhook handler
# -------------------------
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    print("Entering handle_webhook")
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    now = time.time()
    cleanup_processed_messages(now)
    for entry in body.get("entry", []):
        # Messenger payload
        for messaging_event in entry.get("messaging", []):
            message = messaging_event.get("message")
            if not message:
                continue
            message_id = message.get("mid")
            if not message_id or message_id in PROCESSED_MESSAGES:
                continue
            PROCESSED_MESSAGES.add(message_id)
            psid = messaging_event.get("sender", {}).get("id")
            payload = message_payload(
                psid=psid,
                text=message.get("text", ""),
                attachments=message.get("attachments", []),
                timestamp=messaging_event.get("timestamp", now),
            )
            await store_and_broadcast(payload, background_tasks)
        # Instagram Graph webhook payload
        for change in entry.get("changes", []):
            value = change.get("value", {})
            message = value.get("message")
            if not message:
                continue
            message_id = message.get("mid")
            if not message_id or message_id in PROCESSED_MESSAGES:
                continue
            PROCESSED_MESSAGES.add(message_id)
            psid = value.get("from", {}).get("id")
            payload = message_payload(
                psid=psid,
                text=message.get("text", ""),
                attachments=message.get("attachments", []),
                timestamp=value.get("timestamp", now),
            )
            await store_and_broadcast(payload, background_tasks)
    return JSONResponse({"status": "received"})


# Store + WS broadcast


async def store_and_broadcast(payload: dict, background_tasks: BackgroundTasks):
    db_payload = payload.copy()
    try:
        result = await InstagramMessageModel.create(db_payload)
    except Exception:
        logger.exception("Failed to store Instagram message")
        return
    ws_payload = payload.copy()
    ws_payload["id"] = str(result.inserted_id)

    logger.info("📡 IG WS EVENT → %s", ws_payload)

    background_tasks.add_task(
        ws_manager.broadcast_event,
        "instagram.message",
        payload=ws_payload,
    )
    background_tasks.add_task(
        instagram_negotiation_agent,
        payload,
    )
