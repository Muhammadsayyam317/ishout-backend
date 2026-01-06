from fastapi import APIRouter
from app.services.notification_service import admin_ws

router = APIRouter()

router.add_api_websocket_route(
    path="/admin",
    endpoint=admin_ws,
    name="ws_admin",
)
