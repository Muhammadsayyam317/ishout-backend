from datetime import datetime, timezone

from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.websocket_manager import ws_manager


async def save_admin_company_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str | None = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
    create_if_missing: bool = True,
):
    """
    Save one admin<->company message and broadcast it.
    Stored in `config.MONGODB_WHATSAPP_ADMIN_COMPANY`.
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "conversation_mode": "ADMIN_COMPANY",
            "timestamp": timestamp,
        }

        db = get_db()
        collection = db.get_collection(config.MONGODB_WHATSAPP_ADMIN_COMPANY)

        # If we're in webhook routing mode, we may want to avoid creating the
        # admin<->company history when it doesn't exist yet.
        if not create_if_missing:
            exists = await collection.find_one({"thread_id": thread_id}, {"_id": 1})
            if not exists:
                return None

        await collection.insert_one(payload)

        await ws_manager.broadcast_event("whatsapp.message", payload)
        return payload
    except Exception as e:
        print(f"[save_admin_company_message] Error: {e}")
        raise InternalServerErrorException(
            message=f"Error in saving admin company message: {str(e)}"
        ) from e

