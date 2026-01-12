import json
import time
from fastapi import BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from app.config import config
from app.model.Instagram.instagram_message import InstagramMessageModel
from app.services.websocket_manager import ws_manager

PROCESSED_MESSAGES: set = set()


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

    # Clean up processed messages every hour
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
                    continue
                if message_id:
                    PROCESSED_MESSAGES.add(message_id)

                psid = value.get("from", {}).get("id")
                message_data = value["message"]
                text = message_data.get("text", "")
                attachments = message_data.get("attachments", [])

                attachment_list = [
                    {"type": att.get("type"), "url": att.get("payload", {}).get("url")}
                    for att in attachments
                ]

                display_name = f"User_{psid[:8]}" if psid else "Unknown"
                broadcast_data = {
                    "thread_id": psid,
                    "sender": "USER",
                    "platform": "INSTAGRAM",
                    "username": display_name,
                    "message": text if text else "[Attachment]",
                    "timestamp": value.get("timestamp", time.time()),
                    "attachments": attachment_list or [],
                }

                print("📡 IG WS EVENT →", broadcast_data)
                await background_tasks.add_task(
                    ws_manager.broadcast_event,
                    "instagram.message",
                    payload=broadcast_data,
                )
                print("📡 IG WS EVENT SENT →", broadcast_data)

        for messaging_event in entry.get("messaging", []):
            message = messaging_event.get("message")
            if not message or not (message.get("text") or message.get("attachments")):
                continue

            message_id = message.get("mid")
            if message_id and message_id in PROCESSED_MESSAGES:
                continue
            if message_id:
                PROCESSED_MESSAGES.add(message_id)

            sender = messaging_event.get("sender", {})
            psid = sender.get("id")
            text = message.get("text", "")
            attachments = message.get("attachments", [])
            timestamp = messaging_event.get("timestamp", time.time())

            attachment_list = [
                {"type": att.get("type"), "url": att.get("payload", {}).get("url")}
                for att in attachments
            ]

            display_name = f"User_{psid[:8]}" if psid else "Unknown"
            broadcast_data = {
                "thread_id": psid,
                "sender": "USER",
                "platform": "INSTAGRAM",
                "username": display_name,
                "message": text if text else "[Attachment]",
                "timestamp": timestamp,
                "attachments": attachment_list or [],
            }

            print("📡 IG WS EVENT →", broadcast_data)
            await InstagramMessageModel.create(broadcast_data)
            background_tasks.add_task(
                ws_manager.broadcast_event, "instagram.message", payload=broadcast_data
            )
            print("📡 IG WS EVENT SENT →", broadcast_data)
    return JSONResponse({"status": "received"})
