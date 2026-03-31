from datetime import datetime, timezone

from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.websocket_manager import ws_manager


async def save_admin_company_message(
    thread_id: str,
    sender: str,
    message: str,
    username: str | None = None,
    agent_paused: bool = False,
    human_takeover: bool = False,
    conversation_mode: str = "ADMIN_COMPANY",
    create_if_missing: bool = True,
    negotiation_id: str | None = None,
    video_url: str | None = None,
    video_approve_admin: str | None = None,
    video_approve_brand: str | None = None,
    brand_thread_id: str | None = None,
):
    """
    Save one admin<->company message and broadcast it.
    Stored in `config.MONGODB_WHATSAPP_ADMIN_COMPANY`.
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "thread_id": thread_id,
            "username": username,
            "sender": sender,
            "message": message,
            "agent_paused": agent_paused,
            "human_takeover": human_takeover,
            "conversation_mode": conversation_mode,
            "timestamp": timestamp,
        }
        if negotiation_id is not None:
            payload["negotiation_id"] = negotiation_id
        if video_url is not None:
            payload["video_url"] = video_url
        if video_approve_admin is not None:
            payload["video_approve_admin"] = video_approve_admin
        if video_approve_brand is not None:
            payload["video_approve_brand"] = video_approve_brand
        if brand_thread_id is not None:
            payload["brand_thread_id"] = brand_thread_id

        db = get_db()
        collection = db.get_collection(config.MONGODB_WHATSAPP_ADMIN_COMPANY)

        # If we're in webhook routing mode, we may want to avoid creating the
        # admin<->company history when it doesn't exist yet.
        if not create_if_missing:
            exists = await collection.find_one({"thread_id": thread_id}, {"_id": 1})
            if not exists:
                return None

        # For approved-video events, keep one record per negotiation/video and
        # update statuses in-place instead of creating a new document each time.
        if conversation_mode == "ADMIN_COMPANY_VIDEO" and negotiation_id:
            query = {
                "thread_id": thread_id,
                "negotiation_id": negotiation_id,
                "conversation_mode": conversation_mode,
            }
            if video_url is not None:
                query["video_url"] = video_url

            existing_video_doc = await collection.find_one(query, {"_id": 1})
            if existing_video_doc:
                await collection.update_one(
                    {"_id": existing_video_doc["_id"]},
                    {"$set": payload},
                )
            else:
                await collection.insert_one(payload)
        else:
            await collection.insert_one(payload)

        await ws_manager.broadcast_event("whatsapp.message", payload)
        return payload
    except Exception as e:
        print(f"[save_admin_company_message] Error: {e}")
        raise InternalServerErrorException(
            message=f"Error in saving admin company message: {str(e)}"
        ) from e

