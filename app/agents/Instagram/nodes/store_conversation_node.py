from datetime import datetime, timezone
import logging

from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.db.connection import get_db

logger = logging.getLogger(__name__)


async def store_conversation(state: InstagramConversationState):
    print("Entering into Node Store Conversation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    db = get_db()
    conv_collection = db.get_collection("instagram_messages")
    campaign_collection = db.get_collection("campaign_influencers")
    print("Collection Names: ", conv_collection, campaign_collection)
    now = datetime.now(timezone.utc)

    # Conversation binding
    await conv_collection.update_one(
        {"thread_id": state["thread_id"]},
        {
            "$setOnInsert": {
                "thread_id": state["thread_id"],
                "platform": "instagram",
                "influencer_id": state["influencer_id"],
                "campaign_id": state["campaign_id"],
                "negotiation_stage": "INITIAL",
                "ai_enabled": True,
                "created_at": now,
            }
        },
        upsert=True,
    )

    influencer_response = state.get("influencer_response") or {}
    update_payload = {}
    if "rate" in influencer_response:
        update_payload["pricing"] = influencer_response["rate"]

    if "availability" in influencer_response:
        update_payload["availability"] = influencer_response["availability"]

    if update_payload:
        update_payload["updated_at"] = now

        await campaign_collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {"$set": update_payload},
            upsert=True,
        )

    logger.info(
        "Conversation stored | thread=%s influencer=%s campaign=%s",
        state["thread_id"],
        state["influencer_id"],
        state["campaign_id"],
    )
    print("Exiting from Node Store Conversation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
