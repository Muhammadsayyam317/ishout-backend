from datetime import datetime, timedelta, timezone
from app.Schemas.instagram.negotiation_schema import SenderType
from app.config import config
from app.db.connection import get_db
from app.services.whatsapp.onboarding_message import send_whatsapp_message


async def track_unresponsive_users() -> int:
    db = get_db()
    collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": "$thread_id",
                "last_message": {"$first": "$$ROOT"},
            }
        },
        {
            "$match": {
                "last_message.sender_type": SenderType.AI.value,
                "last_message.timestamp": {"$lt": cutoff_time},
            }
        },
    ]

    stale_threads = await collection.aggregate(pipeline).to_list(None)
    if not stale_threads:
        return 0

    for thread in stale_threads:
        thread_id = thread["_id"]
        last_ai_msg = thread["last_message"]

        cursor = collection.find(
            {"thread_id": thread_id},
            sort=[("timestamp", 1)],
        )
        messages = await cursor.to_list(length=20)

        message_text = "\n".join(
            f"{msg['sender_type']}: {msg['message']}" for msg in messages
        )

        await send_whatsapp_message(
            config.ADMIN_PHONE,
            f"🚨 No user response for 24h\n"
            f"Thread: {thread_id}\n"
            f"Last AI message at: {last_ai_msg['timestamp']}\n\n"
            f"{message_text}",
        )

    return len(stale_threads)
