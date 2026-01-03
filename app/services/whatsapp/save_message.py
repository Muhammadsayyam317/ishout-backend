from datetime import datetime, timezone
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def save_conversation_message(
    thread_id: str,
    sender: str,
    message: str,
    campaign_id: str = None,
    username: str = None,
):
    try:
        db = get_db()
        collection = db.get_collection("whatsapp_messages")
        await collection.insert_one(
            {
                "thread_id": thread_id,
                "username": username,
                "sender": sender,
                "message": message,
                "campaign_id": campaign_id,
                "timestamp": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in saving conversation message: {str(e)}"
        ) from e
