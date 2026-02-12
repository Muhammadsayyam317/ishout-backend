from datetime import datetime, timezone
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def save_negotiation_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str | None = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
    conversation_mode: str = "NEGOTIATION",
):
    print("Entering into save_conversation_message")
    try:
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "conversation_mode": conversation_mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        db = get_db()
        collection = db.get_collection("whatsapp_negotiation")
        await collection.insert_one(payload)
        print("Payload: ", payload)
        print("--------------------------------")
        print("Whatsapp Conversation message saved")
        print("--------------------------------")
        return payload

    except Exception as e:
        print("Error in saving conversation message")
        print("--------------------------------")
        print(e)
        print("--------------------------------")
        raise InternalServerErrorException(
            message=f"Error in saving conversation message: {str(e)}"
        ) from e
