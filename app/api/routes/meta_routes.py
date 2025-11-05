from fastapi import APIRouter
from app.api.controllers.meta.webhook import webhook
from app.api.controllers.meta.privacy_policy import get_privacy_policy


router = APIRouter()


router.add_api_route(
    path="/privacy-policy",
    endpoint=get_privacy_policy,
    methods=["GET"],
    tags=["Meta"],
)

router.add_api_route(
    path="/webhook",
    endpoint=webhook,
    methods=["POST"],
    tags=["Meta"],
    name="webhook_post",
)

router.add_api_route(
    path="/webhook",
    endpoint=webhook,
    methods=["GET"],
    tags=["Meta"],
    name="webhook_get",
)
