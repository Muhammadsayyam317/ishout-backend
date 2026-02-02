from typing import Any, Dict
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException, NotFoundException
from app.db.connection import get_db


async def delete_whatsapp_chat(
    thread_id: str,
) -> Dict[str, Any]:
    try:
        db = get_db()
        whatsapp_collection = db.get_collection(
            config.MONGODB_COLLECTION_WHATSAPP_MESSAGES
        )
        whatsapp_sessions_collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS
        )
        Whatsapp_agentcontrol = db.get_collection("agent_controls")
        result = await whatsapp_collection.delete_many({"thread_id": thread_id})
        whatsapp_sessions_result = await whatsapp_sessions_collection.delete_one(
            {"thread_id": thread_id}
        )
        Whatsapp_agentcontrol_result = await Whatsapp_agentcontrol.delete_one(
            {"thread_id": thread_id}
        )
        if result.deleted_count == 0:
            raise NotFoundException(message="Whatsapp messages not found")
        if whatsapp_sessions_result.deleted_count == 0:
            raise NotFoundException(message="Whatsapp sessions not found")
        if Whatsapp_agentcontrol_result.deleted_count == 0:
            raise NotFoundException(message="Whatsapp agent control not found")
        return {"message": "Whatsapp chat deleted successfully"}
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in delete whatsapp chat: {str(e)}"
        ) from e
