from datetime import datetime, timezone
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.websocket_manager import ws_manager


async def save_negotiation_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str | None = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
    message_type: str = "text",
    media_url: str | None = None,
    media_mime_type: str | None = None,
    media_filename: str | None = None,
    conversation_mode: str = "NEGOTIATION",
):
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "message_type": message_type,
            "media_url": media_url,
            "media_mime_type": media_mime_type,
            "media_filename": media_filename,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "conversation_mode": conversation_mode,
            "timestamp": timestamp,
        }

        db = get_db()
        collection = db.get_collection(config.MONGODB_WHATSAPP_NEGOTIATION)
        await collection.insert_one(payload)

        await ws_manager.broadcast_event("whatsapp.message", payload)

        return payload

    except Exception as e:
        print(f"[save_negotiation_message] Error in saving conversation message: {e}")
        raise InternalServerErrorException(
            message=f"Error in saving conversation message: {str(e)}"
        ) from e
