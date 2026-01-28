import datetime
from app.config.credentials_config import config
from app.db.connection import get_db
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message
import logging

logger = logging.getLogger(__name__)


async def store_conversation(state: InstagramConversationState):
    """Upsert conversation binding and influencer details."""
    db = get_db()
    conv_collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)
    campaigns_collection = db.get_collection(
        config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
    )

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
                "created_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )

    # Upsert influencer details if provided
    influencer_details = state.get("influencerResponse")
    if influencer_details:
        await campaigns_collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {
                "$set": {
                    **influencer_details,
                    "updated_at": datetime.now(datetime.timezone.utc),
                }
            },
            upsert=True,
        )

    # Optional: send confirmation message
    if not state.get("final_reply"):
        confirmation = "Thanks for sharing your details! We'll get back to you shortly."
        await Send_Insta_Message(
            message=confirmation,
            recipient_id=state["thread_id"],
        )
        state["final_reply"] = confirmation

    logger.debug(f"Conversation stored for thread {state['thread_id']}")
    return state
