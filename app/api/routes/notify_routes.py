from fastapi import APIRouter, Depends
from typing import Any, Dict
from pydantic import BaseModel
from app.middleware.auth_middleware import require_admin_access
from app.services.notification_service import send_notification, broadcast_notification


class NotifyPayload(BaseModel):
    user_id: str | None = None
    title: str
    message: str
    data: Dict[str, Any] | None = None


router = APIRouter(prefix="/api", tags=["Notifications"])


@router.post("/notify")
async def notify(payload: NotifyPayload, _=Depends(require_admin_access)):
    body = {"title": payload.title, "message": payload.message}
    if payload.data:
        body["data"] = payload.data

    if payload.user_id:
        result = await send_notification(payload.user_id, body)
    else:
        result = await broadcast_notification(body)

    return {"status": "ok", **result}
