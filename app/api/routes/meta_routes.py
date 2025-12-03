from fastapi import APIRouter
from app.api.controllers.meta.notification import (
    handle_webhook,
    verify_webhook,
    websocket_notifications,
)
from app.api.controllers.meta.privacy_policy import get_privacy_policy
from app.api.controllers.meta.whatsapp_webhook import verify_whatsapp_webhook
from app.agents.whatsapp_agent import handle_whatsapp_events
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp

router = APIRouter()

router.add_api_route(
    path="/privacy-policy",
    endpoint=get_privacy_policy,
    methods=["GET"],
    tags=["Meta"],
)

router.add_api_route(
    path="/meta",
    endpoint=verify_webhook,
    methods=["GET"],
    tags=["Meta"],
)

router.add_api_route(
    path="/meta",
    endpoint=handle_webhook,
    methods=["POST"],
    tags=["Meta"],
),

router.add_api_websocket_route(
    path="/notifications",
    endpoint=websocket_notifications,
    name="meta_notifications",
)


router.add_api_route(
    path="/whatsapp-webhook",
    endpoint=verify_whatsapp_webhook,
    methods=["GET"],
    tags=["Meta"],
    name="verify_whatsapp_webhook",
)

router.add_api_route(
    path="/whatsapp-webhook",
    endpoint=handle_whatsapp_events,
    methods=["POST"],
    tags=["Meta"],
    name="handle_whatsapp_events",
)
