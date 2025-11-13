from fastapi import APIRouter
from app.api.controllers.meta.notification import (
    handle_webhook,
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

router.add_api_route(
    path="/notifications",
    endpoint=websocket_notifications,
    methods=["websocket"],
    tags=["Meta"],
)
