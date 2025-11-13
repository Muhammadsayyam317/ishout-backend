from fastapi import APIRouter
from app.api.controllers.meta.notification import (
    handle_webhook,
    send_notification_to_user,
    verify_webhook,
    websocket_notifications,
)
from app.api.controllers.meta.privacy_policy import get_privacy_policy

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
    path="/send-notification",
    endpoint=send_notification_to_user,
    methods=["POST"],
    tags=["Meta"],
),
