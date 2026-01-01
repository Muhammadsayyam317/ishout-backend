import time
from app.agents.state.create_user_state import create_new_state
from app.core.exception import InternalServerErrorException
from app.db.mongo_session import get_session_collection

SESSION_EXPIRY_SECONDS = 600


async def get_user_state(sender_id):
    print("Entering get_user_state")
    try:
        print(f"Getting user state for sender_id: {sender_id}")
        session_collection = get_session_collection()
        state = await session_collection.find_one({"sender_id": sender_id})
        print(f"State: {state}")
        if state:
            state.pop("_id", None)
        print(f"State after pop: {state}")
        now = time.time()
        if not state or now - state.get("last_active", 0) > SESSION_EXPIRY_SECONDS:
            return await create_new_state(sender_id)
        print("Updating user state")
        await session_collection.update_one(
            {"sender_id": sender_id}, {"$set": {"last_active": now}}
        )
        state["last_active"] = now
        print(f"Exiting get_user_state with state: {state}")
        return state
    except Exception as e:
        print("Exiting get_user_state with error")
        print(f"Error getting user state: {e}")
        raise InternalServerErrorException(
            message=f"Error getting user state: {e}"
        ) from e
