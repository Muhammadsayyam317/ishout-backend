from datetime import datetime, timezone
from app.services.websocket_manager import ws_manager


async def broadcast_user_message(*, thread_id: str, message: str):
    await ws_manager.broadcast_event(
        "whatsapp.message",
        {
            "thread_id": thread_id,
            "sender": "USER",
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
