from fastapi import Request
from app.config.credentials_config import config
from fastapi import Response


async def verify_whatsapp_webhook(request: Request):
    params = request.query_params
    if "hub.mode" not in params:
        return Response(content="WhatsApp Webhook is active", status_code=200)

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.META_VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)
