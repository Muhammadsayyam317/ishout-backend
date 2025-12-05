import time
from app.db.mongo_session import get_session_collection

SESSION_EXPIRY_SECONDS = 600


async def create_new_state(sender_id):
    session_collection = get_session_collection()
    new_state = {
        "sender_id": sender_id,
        "platform": None,
        "country": None,
        "category": None,
        "number_of_influencers": None,
        "user_message": None,
        "reply": None,
        "last_active": time.time(),
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
    new_data.pop("_id", None)
    session_collection = get_session_collection()
    existing = await session_collection.find_one({"sender_id": sender_id}) or {}

    update_fields = {}
    for key, value in new_data.items():
        if value is not None:
            update_fields[key] = value

    for key in existing:
        if key not in update_fields:
            update_fields[key] = existing[key]

    update_fields["last_active"] = time.time()

    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": update_fields}, upsert=True
    )

    updated = await session_collection.find_one({"sender_id": sender_id})
    updated.pop("_id", None)
    return updated


async def reset_user_state(sender_id):
    return await create_new_state(sender_id)
