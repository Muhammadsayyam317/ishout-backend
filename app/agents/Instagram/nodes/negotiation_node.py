from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    SenderType,
)
from app.agents.Instagram.graph.instagram_graph import instagram_graph
from app.config.credentials_config import config
from app.db.connection import get_db


async def negotiation(payload: dict):
    if payload["sender_type"] == SenderType.AI:
        return

    db = get_db()
    conv = await db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION).find_one(
        {"thread_id": payload["thread_id"], "ai_enabled": True}
    )

    if not conv:
        return None

    state = InstagramConversationState(
        thread_id=payload["thread_id"],
        user_message=payload["message"],
        sender_type=payload["sender_type"],
        influencer_id=conv["influencer_id"],
        campaign_id=conv["campaign_id"],
        min_price=conv["min_price"],
        max_price=conv["max_price"],
    )

    result = await instagram_graph.ainvoke(state)
    reply = result.get("reply")

    return reply
