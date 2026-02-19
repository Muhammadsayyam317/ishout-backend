from datetime import datetime, timezone
from app.db.connection import get_db


async def update_negotiation_state(thread_id: str, data: dict):
    print("Entering into update Negotiation State")
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")
    data.pop("_id", None)
    data["_updated_at"] = datetime.now(timezone.utc)
    await collection.update_one({"thread_id": thread_id}, {"$set": data}, upsert=True)
    print("Negotiation State updated successfully")
    print(f"Negotiation State: {await collection.find_one({"thread_id": thread_id})}")
    print("Exiting from update Negotiation State")
    return await collection.find_one({"thread_id": thread_id})


async def get_negotiation_state(thread_id: str):
    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")
    return await collection.find_one({"thread_id": thread_id})
