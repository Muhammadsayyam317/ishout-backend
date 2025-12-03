from datetime import datetime
from typing import List, Dict
from fastapi import Request

from app.db.connection import get_db


async def save_chat_message(
    thread_id: str, role: str, content: str, metadata: Dict | None = None
) -> None:
    db = get_db()
    doc = {
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(),
    }
    if metadata:
        doc["metadata"] = metadata

    await db["whatsapp"].insert_one(doc)


async def get_chat_history_messages(request: Request, thread_id: str) -> List[Dict]:
    db = get_db()
    messages: List[Dict] = []

    try:
        cursor = db["whatsapp"].find({"thread_id": thread_id}).sort("created_at", 1)
        async for doc in cursor:
            messages.append(
                {
                    "role": doc.get("role", ""),
                    "content": doc.get("content", ""),
                    "created_at": doc.get("created_at"),
                }
            )
        print(f"Loaded {len(messages)} messages for session {thread_id}")
    except Exception as e:
        print(
            f"Error retrieving chat history for session {thread_id} from MongoDB: {e}"
        )

    return messages
