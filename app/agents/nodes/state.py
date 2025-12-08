import time
from datetime import datetime
from app.db.mongo_session import get_session_collection

SESSION_EXPIRY_SECONDS = 600


async def create_new_state(sender_id):
    session_collection = get_session_collection()
    new_state = {
        "sender_id": sender_id,
        "platform": [],
        "category": [],
        "country": [],
        "limit": None,
        "followers": [],
        "user_message": None,
        "reply": None,
        "last_active": datetime.now(),
        "done": False,
        "reply_sent": False,
        "campaign_id": None,
        "campaign_created": False,
    }
    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": new_state}, upsert=True
    )
    return new_state


async def get_user_state(sender_id):
    session_collection = get_session_collection()
    state = await session_collection.find_one({"sender_id": sender_id})
    if state:
        state.pop("_id", None)

    now = time.time()
    if not state or now - state.get("last_active", 0) > SESSION_EXPIRY_SECONDS:
        return await create_new_state(sender_id)
    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": {"last_active": now}}
    )
    state["last_active"] = now
    return state


async def update_user_state(sender_id, new_data: dict):
    session_collection = get_session_collection()

    new_data.pop("_id", None)
    new_data["last_active"] = time.time()

    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": new_data}, upsert=True
    )

    updated = await session_collection.find_one({"sender_id": sender_id})
    updated.pop("_id", None)
    return updated


async def reset_user_state(sender_id):
    return await create_new_state(sender_id)
