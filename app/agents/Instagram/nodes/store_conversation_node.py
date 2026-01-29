from datetime import datetime, timezone
import logging

from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.db.connection import get_db
from app.services.instagram.send_instagram_message import Send_Insta_Message
from app.config.credentials_config import config

logger = logging.getLogger(__name__)


async def store_conversation(state: InstagramConversationState):
    print("Entering into Node Store Conversation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    db = get_db()
    conv_collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)
    campaign_collection = db.get_collection(
        config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
    )
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

    influencer_response = state.get("influencerResponse") or {}
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
    # Optional confirmation reply
    if not state.get("final_reply"):
        confirmation = (
            "Thanks for sharing the details! "
            "I'll review this and get back to you shortly."
        )
        await Send_Insta_Message(
            message=confirmation,
            recipient_id=state["thread_id"],
        )
        state["final_reply"] = confirmation

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
