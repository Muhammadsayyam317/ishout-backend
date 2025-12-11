from fastapi import HTTPException
from app.db.connection import get_db
from pymongo import ReturnDocument
import time


async def create_whatsapp_user(sender_id: str, name: str = None):
    try:
        db = get_db()
        whatsapp_users = db.get_collection("whatsapp_users")

        update_doc = {
            "$set": {
                "last_seen": time.time(),
                "updated_at": time.time(),
            },
            "$setOnInsert": {
                "sender_id": sender_id,
                "created_at": time.time(),
                "first_seen": time.time(),
                "name": name,
            },
        }

        user = await whatsapp_users.find_one_and_update(
            {"sender_id": sender_id},
            update_doc,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating/updating WhatsApp user: {str(e)}",
        ) from e
