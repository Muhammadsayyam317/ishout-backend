from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Request
from app.api.controllers.meta.webhook import (
    webhook,
    debug_state,
    DMRequest,
    send_dm,
    mock_webhook,
)
from fastapi.responses import Response
from app.api.controllers.meta.privacy_policy import get_privacy_policy
from app.services.websocket_manager import ws_manager

router = APIRouter()
VERIFY_TOKEN = "longrandomstring123"


router.add_api_route(
    path="/privacy-policy",
    endpoint=get_privacy_policy,
    methods=["GET"],
    tags=["Meta"],
)


@router.get("/meta")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Meta Webhook verified successfully.")
        return Response(content=challenge, status_code=200)
    else:
        print(" Meta Webhook verification failed.")
        return Response(status_code=403)


@router.post("/meta")
async def meta_webhook(
    request: Request, background_tasks: BackgroundTasks = BackgroundTasks()
):
    return await webhook(request, background_tasks)


# @router.post("/meta")
# async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
#     body = await request.json()
#     print("📩 Incoming Meta Webhook:", body)

#     for entry in body.get("entry", []):
#         for messaging in entry.get("messaging", []):
#             message = messaging.get("message", {})
#             sender = messaging.get("sender", {}).get("id")
#             if message and "text" in message:
#                 await ws_manager.broadcast(
#                     {
#                         "type": "ig_reply",
#                         "from_psid": sender,
#                         "text": message["text"],
#                     }
#                 )
#     return {"status": "ok"}


# Debug endpoints (consider protecting with auth in prod)
@router.get("/debug/state")
async def meta_debug_state(limit: int = 5):
    return await debug_state(limit)


@router.post("/dm")
async def meta_send_dm(body: DMRequest):
    return await send_dm(body)


@router.post("/debug/mock-webhook")
async def meta_mock_webhook():
    # Creates a fake inbound message so you can test your inbox UI without Meta
    return await mock_webhook({})
