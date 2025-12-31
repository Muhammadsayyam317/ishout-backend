from datetime import datetime, timezone
from app.db.connection import get_db


async def save_conversation_message(
    thread_id: str,
    sender: str,
    message: str,
    node: str = None,
    campaign_id: str = None,
    meta: dict = None,
):
    db = get_db()
    collection = db.get_collection("whatsapp_messages")

    await collection.insert_one(
        {
            "thread_id": thread_id,
            "sender": sender,
            "message": message,
            "node": node,
            "campaign_id": campaign_id,
            "meta": meta or {},
            "timestamp": datetime.now(timezone.utc),
        }
    )
