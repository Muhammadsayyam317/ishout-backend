import time
from app.db.connection import get_db

SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def create_new_state(sender_id: str):
    return {
        "sender_id": sender_id,
        "platform": None,
        "country": None,
        "category": None,
        "number_of_influencers": None,
        "user_message": None,
        "reply": None,
        "last_active": time.time(),
    }


async def get_user_state(sender_id: str):
    """Fetch state from MongoDB using shared connection, auto-create or auto-reset."""
    db = get_db()
    sessions = db["whatsapp_sessions"]
    now = time.time()
    state = await sessions.find_one({"sender_id": sender_id})

    # 🟢 New user → create state
    if not state:
        new_state = create_new_state(sender_id)
        await sessions.insert_one(new_state)
        return new_state

    # ⏳ Session expired → reset
    if now - state.get("last_active", 0) > SESSION_EXPIRY_SECONDS:
        new_state = create_new_state(sender_id)
        await sessions.update_one({"sender_id": sender_id}, {"$set": new_state})
        return new_state

    # 🔄 Always update last_active
    await sessions.update_one({"sender_id": sender_id}, {"$set": {"last_active": now}})
    # Return fresh updated state
    return await sessions.find_one({"sender_id": sender_id})


async def update_user_state(sender_id: str, new_data: dict):
    """Merge new data into existing state and save to MongoDB."""
    db = get_db()
    sessions = db["whatsapp_sessions"]

    await get_user_state(sender_id)  # ensure session exists

    update_payload = {k: v for k, v in new_data.items() if v is not None}
    update_payload["last_active"] = time.time()

    await sessions.update_one({"sender_id": sender_id}, {"$set": update_payload})
    return await sessions.find_one({"sender_id": sender_id})


async def reset_user_state(sender_id: str):
    """Reset full session state."""
    db = get_db()
    sessions = db["whatsapp_sessions"]
    new_state = create_new_state(sender_id)
    await sessions.update_one({"sender_id": sender_id}, {"$set": new_state})
    return new_state
