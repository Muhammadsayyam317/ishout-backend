import time
from app.agents.Whatsapp.state.create_user_state import create_new_state
from app.core.exception import InternalServerErrorException
from app.db.mongo_session import get_session_collection

SESSION_EXPIRY_SECONDS = 600


async def get_user_state(sender_id):
    try:
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
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error getting user state: {e}"
        ) from e
