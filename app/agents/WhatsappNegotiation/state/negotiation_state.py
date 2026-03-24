from datetime import datetime, timezone
from app.db.connection import get_db
from typing import Optional
from app.core.exception import InternalServerErrorException
from app.config.credentials_config import config


async def update_negotiation_state(thread_id: str, data: dict) -> Optional[dict]:
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_NEGOTIATION_AGENT_CONTROLS)
        data.pop("_id", None)
        data["_updated_at"] = datetime.now(timezone.utc)

        await collection.update_one(
            {"thread_id": thread_id},
            {"$set": data},
            upsert=True,
        )

        return await collection.find_one({"thread_id": thread_id})

    except Exception as e:
        print(f"[update_negotiation_state] Failed: {e}")
        raise InternalServerErrorException(
            message=f"Error updating negotiation state: {str(e)}"
        ) from e


async def get_negotiation_state(thread_id: str) -> Optional[dict]:
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_NEGOTIATION_AGENT_CONTROLS)
        return await collection.find_one({"thread_id": thread_id})
    except Exception as e:
        print(f"[get_negotiation_state] Failed: {e}")
        raise InternalServerErrorException(
            message=f"Error fetching negotiation state: {str(e)}"
        ) from e
