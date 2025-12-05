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
    }

    await session_collection.update_one(
        {"sender_id": sender_id},
        {"$set": new_state},
        upsert=True,
    )

    return new_state


async def get_user_state(sender_id):
    session_collection = get_session_collection()
    state = await session_collection.find_one({"sender_id": sender_id})
    if state:
        state.pop("_id", None)
    if not state:
        return await create_new_state(sender_id)
    now = time.time()
    last_active = state.get("last_active", 0)
    if now - last_active > SESSION_EXPIRY_SECONDS:
        return await create_new_state(sender_id)
    await session_collection.update_one(
        {"sender_id": sender_id},
        {"$set": {"last_active": now}},
    )

    state["last_active"] = now
    state.pop("_id", None)
    return state


async def update_user_state(sender_id, new_data: dict):
    new_data.pop("_id", None)
    session_collection = get_session_collection()
    allowed_fields = [
        "platform",
        "country",
        "category",
        "number_of_influencers",
        "user_message",
        "reply",
        "last_active",
        "done",
        "reply_sent",
        "campaign_id",
        "campaign_created",
    ]

    update_fields = {field: new_data.get(field) for field in allowed_fields}
    update_fields["last_active"] = time.time()

    await session_collection.update_one(
        {"sender_id": sender_id},
        {"$set": update_fields},
        upsert=True,
    )

    updated = await session_collection.find_one({"sender_id": sender_id})
    updated.pop("_id", None)
    return updated


async def reset_user_state(sender_id):
    return await create_new_state(sender_id)
