from datetime import datetime, timezone
from app.db.connection import get_db


async def update_negotiation_state(thread_id: str, data: dict):
    """
    Updates the negotiation state in MongoDB.
    Adds a timestamp for tracking last update.
    """
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")

    data["_updated_at"] = datetime.now(timezone.utc)

    try:
        await collection.update_one(
            {"thread_id": thread_id},
            {"$set": data},
            upsert=True,
        )
    except Exception as e:
        print(f"[update_negotiation_state] Failed for {thread_id}: {e}")
        raise


async def get_negotiation_state(thread_id: str):
    """
    Retrieves the negotiation state from MongoDB.
    Returns an empty dict if no state exists.
    """
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")

    try:
        doc = await collection.find_one({"thread_id": thread_id})
        return doc or {}
    except Exception as e:
        print(f"[get_negotiation_state] Failed for {thread_id}: {e}")
        return {}
