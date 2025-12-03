import time
from app.db.connection import get_db
from typing import Dict, Any


SESSION_EXPIRY_SECONDS = 600  # 10 minutes
SESSIONS_COLLECTION = "whatsapp_sessions"


def _create_new_state(sender_id: str) -> Dict[str, Any]:
    now = time.time()
    return {
        "sender_id": sender_id,
        "platform": None,
        "country": None,
        "category": None,
        "number_of_influencers": None,
        "user_message": None,
        "reply": None,
        "last_active": now,
        "last_message_id": None,  # for idempotency
    }


async def get_user_state(sender_id: str) -> Dict[str, Any]:
    db = get_db()
    sessions = db[SESSIONS_COLLECTION]
    now = time.time()

    state = await sessions.find_one({"sender_id": sender_id})
    if not state:
        new_state = _create_new_state(sender_id)
        await sessions.insert_one(new_state)
        return new_state

    # expire?
    if now - state.get("last_active", 0) > SESSION_EXPIRY_SECONDS:
        new_state = _create_new_state(sender_id)
        await sessions.update_one({"sender_id": sender_id}, {"$set": new_state})
        return new_state

    # update last_active
    await sessions.update_one({"sender_id": sender_id}, {"$set": {"last_active": now}})
    return await sessions.find_one({"sender_id": sender_id})


async def update_user_state(sender_id: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_db()
    sessions = db[SESSIONS_COLLECTION]
    await get_user_state(sender_id)
    payload = {k: v for k, v in new_data.items() if v is not None}
    payload["last_active"] = time.time()
    await sessions.update_one({"sender_id": sender_id}, {"$set": payload})
    return await sessions.find_one({"sender_id": sender_id})


async def reset_user_state(sender_id: str) -> Dict[str, Any]:
    db = get_db()
    sessions = db[SESSIONS_COLLECTION]
    new_state = _create_new_state(sender_id)
    await sessions.update_one(
        {"sender_id": sender_id}, {"$set": new_state}, upsert=True
    )
    return new_state
