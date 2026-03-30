from datetime import datetime, timezone
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.websocket_manager import ws_manager


async def save_conversation_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str | None = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
    conversation_mode: str = "DEFAULT",
):

    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "timestamp": timestamp,
            "conversation_mode": conversation_mode,
        }

        db = get_db()
        collection = db.get_collection(config.MONGODB_COLLECTION_WHATSAPP_MESSAGES)
        await collection.insert_one(payload)

        await ws_manager.broadcast_event("whatsapp.message", payload)

        return payload

    except Exception as e:
        print(f"[save_conversation_message] Error in saving conversation message: {e}")
        raise InternalServerErrorException(
            message=f"Error in saving conversation message: {str(e)}"
        ) from e
