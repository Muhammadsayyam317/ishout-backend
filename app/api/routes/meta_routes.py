from fastapi import APIRouter, BackgroundTasks, Request
from app.api.controllers.meta.webhook import webhook, debug_state, DMRequest, send_dm, mock_webhook
from app.api.controllers.meta.privacy_policy import get_privacy_policy


router = APIRouter()


router.add_api_route(
    path="/privacy-policy",
    endpoint=get_privacy_policy,
    methods=["GET"],
    tags=["Meta"],
)

# router.add_api_route(
#     path="/webhook",
#     endpoint=webhook,
#     methods=["POST"],
#     tags=["Meta"],
#     name="webhook_post",
# )
#
# router.add_api_route(
#     path="/webhook",
#     endpoint=webhook,
#     methods=["GET"],
#     tags=["Meta"],
#     name="webhook_get",
# )


@router.api_route("/meta", methods=["GET", "POST"])
async def meta_webhook(request: Request, background_tasks: BackgroundTasks):
    return await webhook(request, background_tasks)



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
