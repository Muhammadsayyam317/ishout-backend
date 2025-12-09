from fastapi import HTTPException
from app.db.connection import get_db
from pymongo import ReturnDocument
import time


async def create_whatsapp_user(
    sender_id: str, name: str = None, increment_messages: bool = True
):
    try:
        db = get_db()
        whatsapp_users = db.get_collection("whatsapp_users")
        update_doc = {
            "$setOnInsert": {
                "sender_id": sender_id,
                "first_seen": time.time(),
                "campaign_count": 0,
                "campaign_ids": [],
                "total_messages": 0,
                "is_blocked": False,
                "created_at": time.time(),
            },
            "$set": {
                "last_seen": time.time(),
                "updated_at": time.time(),
            },
            "$inc": {},
        }

        if name:
            update_doc["$set"]["name"] = name

        if increment_messages:
            update_doc["$inc"]["total_messages"] = 1

        update_doc["$inc"]["campaign_count"] = update_doc["$inc"].get(
            "campaign_count", 1
        )

        user = await whatsapp_users.find_one_and_update(
            {"sender_id": sender_id},
            update_doc,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating/updating WhatsApp user: {str(e)}",
        ) from e
