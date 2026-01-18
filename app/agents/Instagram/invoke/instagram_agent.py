from time import timezone
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    SenderType,
)
from app.agents.Instagram.graph.instagram_graph import instagram_graph
from app.config.credentials_config import config
from app.db.connection import get_db
from app.model.Instagram.instagram_message import InstagramMessageModel
from app.services.instagram.send_instagram_message import Send_Insta_Message
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def instagram_negotiation_agent(payload: dict):
    print("Enter into Instagram Negotiation Agent")
    if payload["sender_type"] == SenderType.AI:
        logger.info("🛑 Ignoring AI/admin message")
        print("Exiting from Instagram Negotiation Agent")
        return None

    db = get_db()
    conv = await db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION).find_one(
        {"thread_id": payload["thread_id"]}
    )

    if not conv:
        logger.warning(f"No conversation found for thread_id {payload['thread_id']}")
        return None

    state = InstagramConversationState(
        thread_id=payload["thread_id"],
        user_message=payload["message"],
        sender_type=payload["sender_type"],
        influencer_id=conv.get("influencer_id"),
        campaign_id=conv.get("campaign_id"),
        min_price=conv.get("min_price"),
        max_price=conv.get("max_price"),
        stage=conv.get("negotiation_stage", "INITIAL"),
    )

    result = await instagram_graph.ainvoke(state)
    reply_obj = getattr(result, "reply", None)
    if not reply_obj:
        reply_obj = result.get("reply") if isinstance(result, dict) else None

    if not reply_obj:
        logger.info("No AI reply generated, skipping send")
        return None

    ai_message_text = (
        reply_obj
        if isinstance(reply_obj, str)
        else getattr(reply_obj, "reply", str(reply_obj))
    )

    await Send_Insta_Message(
        message=ai_message_text,
        recipient_id=payload["thread_id"],
    )
    db_payload = {
        "thread_id": payload["thread_id"],
        "sender_type": SenderType.AI.value,
        "message": ai_message_text,
        "timestamp": datetime.now(timezone.utc),
        "attachments": [],
    }
    result = await InstagramMessageModel.create(db_payload)
    logger.info(
        f"Stored AI reply for thread {payload['thread_id']} with ID {result.inserted_id}"
    )
    print("Exiting from Instagram Negotiation Agent")
    return reply_obj
