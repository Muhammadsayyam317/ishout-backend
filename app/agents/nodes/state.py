from app.agents.whatsapp_agent import USER_STATES
import time


SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def create_new_state(sender_id):
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


def get_user_state(sender_id):
    """Return state or create/reset it if expired."""
    now = time.time()

    # create new state for new user
    if sender_id not in USER_STATES:
        USER_STATES[sender_id] = create_new_state(sender_id)
        return USER_STATES[sender_id]

    state = USER_STATES[sender_id]

    # check expiry
    if now - state.get("last_active", 0) > SESSION_EXPIRY_SECONDS:
        USER_STATES[sender_id] = create_new_state(sender_id)

    # always update last_active
    USER_STATES[sender_id]["last_active"] = now
    return USER_STATES[sender_id]


def update_user_state(sender_id, new_data: dict):
    state = get_user_state(sender_id)
    for key, value in new_data.items():
        if value is not None:
            state[key] = value
    state["last_active"] = time.time()
    return state


def reset_user_state(sender_id):
    USER_STATES[sender_id] = create_new_state(sender_id)
