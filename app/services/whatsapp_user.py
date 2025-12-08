from fastapi import HTTPException
from app.db.connection import get_db
from pymongo import ReturnDocument
from datetime import datetime, timezone


async def create_whatsapp_user(sender_id: str, name: str = None):
    try:
        db = get_db()
        whatsapp_users = db.get_collection("whatsapp_users")
        now = datetime.now(timezone.utc)
        set_data = {"last_seen": now, "updated_at": now}

        if name:
            set_data["name"] = name

        user = await whatsapp_users.find_one_and_update(
            {"sender_id": sender_id},
            {
                "$setOnInsert": {
                    "sender_id": sender_id,
                    "first_seen": now,
                    "created_at": now,
                    "campaign_count": 0,
                    "campaign_ids": [],
                    "total_messages": 0,
                    "is_blocked": False,
                },
                "$set": set_data,
                "$inc": {"total_messages": 1},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating/updating WhatsApp user: {str(e)}",
        )
