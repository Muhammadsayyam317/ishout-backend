import time
from app.db.mongo_session import get_session_collection


async def create_new_state(sender_id):
    session_collection = get_session_collection()
    existing_state = await session_collection.find_one({"sender_id": sender_id})
    conversation_round = (
        existing_state.get("conversation_round", 0) if existing_state else 0
    )

    new_state = {
        "sender_id": sender_id,
        "platform": [],
        "category": [],
        "country": [],
        "limit": None,
        "followers": [],
        "user_message": None,
        "reply": None,
        "name": None,
        "last_active": time.time(),
        "done": False,
        "reply_sent": False,
        "campaign_id": None,
        "campaign_created": False,
        "ready_for_campaign": False,
        "acknowledged": False,
        "conversation_round": conversation_round,
    }
    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": new_state}, upsert=True
    )
    return new_state
