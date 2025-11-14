import json
import time
from fastapi import BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response
from app.services.websocket_manager import ws_manager
from app.config import config


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
        # Handle Instagram Direct format: entry[].changes[].value
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
                background_tasks.add_task(
                    ws_manager.broadcast,
                    {
                        "type": "ig_reply",
                        "from_psid": sender.get("id"),
                        "to_page_id": recipient.get("id"),
                        "from_username": None,  # Username not available in messaging format
                        "text": message.get("text", ""),
                        "timestamp": messaging_event.get("timestamp", time.time()),
                    },
                )

    return JSONResponse({"status": "received"})
