import time
from app.db.mongo_session import get_session_collection


async def update_user_state(sender_id, new_data: dict):
    print("Entering into update_user_state")
    print("--------------------------------")
    print(sender_id)
    print("--------------------------------")
    print(new_data)
    print("--------------------------------")
    session_collection = get_session_collection()
    new_data.pop("_id", None)
    new_data["last_active"] = time.time()
    await session_collection.update_one(
        {"sender_id": sender_id}, {"$set": new_data}, upsert=True
    )
    updated = await session_collection.find_one({"sender_id": sender_id})
    updated.pop("_id", None)
    print("Updated state")
    print("--------------------------------")
    print(updated)
    print("--------------------------------")
    return updated
