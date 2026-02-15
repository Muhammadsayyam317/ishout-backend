from fastapi import APIRouter
from app.api.controllers.meta.privacy_policy import get_privacy_policy
from app.api.controllers.meta.whatsapp_webhook import verify_whatsapp_webhook
from app.agents.Whatsapp.invoke.whatsapp_agent import handle_whatsapp_events
from app.services.instagram.Instagram_ws_notification import (
    handle_webhook,
    verify_webhook,
)

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

# router.add_api_route(
#     path="",
#     endpoint=instagram_callback,
#     methods=["GET"],
#     tags=["Meta"],
#     name="instagram_callback",
# )
