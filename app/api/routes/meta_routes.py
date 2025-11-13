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


# GET verification
@router.get("/meta")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Meta Webhook verified successfully.")
        return Response(content=challenge, status_code=200)

    print("❌ Meta Webhook verification failed.")
    return Response(status_code=403)


# POST notifications (from Meta)
@router.post("/meta")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print("📩 Incoming Meta Webhook POST:", body)
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            if "message" in value:
                await webhook(request, background_tasks)
                # await ws_manager.broadcast(
                #     {
                #         "type": "ig_reply",
                #         "from_username": value.get("from", {}).get(
                #             "username", "unknown"
                #         ),
                #         "text": value["message"].get("text", ""),
                #         "timestamp": value.get("timestamp"),
                #     }
                # )

    return {"status": "received"}


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
