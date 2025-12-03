from datetime import datetime
from typing import Dict
from app.db.connection import get_db


async def save_chat_message(
    thread_id: str, role: str, content: str, metadata: Dict | None = None
):
    db = get_db()
    doc = {
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow(),
    }
    if metadata:
        doc["metadata"] = metadata
    await db["whatsapp_messages"].insert_one(doc)
