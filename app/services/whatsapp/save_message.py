from datetime import datetime, timezone
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def save_conversation_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
):
    try:
        print(
            f"Saving conversation message: {thread_id}, {sender}, {message}, {username}, {agent_paused}, {human_takeover}"
        )
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        print(f"Payload: {payload}")
        db = get_db()
        collection = db.get_collection("whatsapp_messages")
        await collection.insert_one(payload)
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in saving conversation message: {str(e)}"
        ) from e
