from datetime import datetime, timezone
from app.db.connection import get_db
from typing import Optional

from app.utils.printcolors import Colors


async def update_negotiation_state(thread_id: str, data: dict) -> Optional[dict]:
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")
    data["_updated_at"] = datetime.now(timezone.utc)
    try:
        await collection.update_one(
            {"thread_id": thread_id},
            {"$set": data},
            upsert=True,
        )
        updated_doc = await collection.find_one({"thread_id": thread_id})
        return updated_doc
    except Exception as e:
        print(f"{Colors.RED}[update_negotiation_state] Failed for {thread_id}: {e}")
        raise


async def get_negotiation_state(thread_id: str) -> Optional[dict]:
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")

    try:
        doc = await collection.find_one({"thread_id": thread_id})
        return doc
    except Exception as e:
        print(f"{Colors.RED}[get_negotiation_state] Failed for {thread_id}: {e}")
        return None
