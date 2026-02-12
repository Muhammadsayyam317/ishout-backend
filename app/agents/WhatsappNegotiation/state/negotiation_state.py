from datetime import datetime, timezone
from app.db.connection import get_db


async def update_negotiation_state(thread_id: str, data: dict):
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
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")

    try:
        doc = await collection.find_one({"thread_id": thread_id})
        return doc
    except Exception as e:
        print(f"[get_negotiation_state] Failed for {thread_id}: {e}")
        return None
