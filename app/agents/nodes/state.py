import time
from app.db.mongo_session import get_session_collection

SESSION_EXPIRY_SECONDS = 600


def create_new_state(sender_id):
    """Create a fresh session document."""
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
    session_collection.update_one(
        {"sender_id": sender_id}, {"$set": new_state}, upsert=True
    )
    return new_state


def get_user_state(sender_id):
    """Fetch user session from DB; create if missing or expired."""
    session_collection = get_session_collection()
    state = session_collection.find_one({"sender_id": sender_id})

    # If no session → create new
    if not state:
        return create_new_state(sender_id)

    # Check if expired
    now = time.time()
    last_active = state.get("last_active", 0)

    if now - last_active > SESSION_EXPIRY_SECONDS:
        return create_new_state(sender_id)

    # Update last_active
    session_collection.update_one(
        {"sender_id": sender_id}, {"$set": {"last_active": now}}
    )

    # Return updated state
    state["last_active"] = now
    return state


def update_user_state(sender_id, new_data: dict):
    """Update values inside the MongoDB session."""
    session_collection = get_session_collection()
    now = time.time()

    update_fields = {key: value for key, value in new_data.items() if value is not None}
    update_fields["last_active"] = now

    session_collection.update_one({"sender_id": sender_id}, {"$set": update_fields})

    return session_collection.find_one({"sender_id": sender_id})


def reset_user_state(sender_id):
    """Manually reset session."""
    return create_new_state(sender_id)
