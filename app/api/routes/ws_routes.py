from fastapi import APIRouter
from app.api.controllers.meta.notification import websocket_notifications

router = APIRouter()

router.add_api_websocket_route(
    path="/notifications",
    endpoint=websocket_notifications,
    name="ws_notifications",
)
