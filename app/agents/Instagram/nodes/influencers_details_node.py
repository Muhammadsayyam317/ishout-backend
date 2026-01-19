from pydantic import BaseModel
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.instagram.send_instagram_message import Send_Insta_Message
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class InfluencerDetailsInput(BaseModel):
    rate: float
    currency: str
    content_type: str
    content_format: str
    content_length: int
    content_duration: int
    availability: str


async def influencers_details_node(
    state: InstagramConversationState,
    details: InfluencerDetailsInput,
) -> InstagramConversationState:
    print("Enter into Influencers Details Node")
    try:
        db = get_db()
        campaigns_collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )

        update_data = {
            "rate": details.rate,
            "currency": details.currency,
            "content_type": details.content_type,
            "content_format": details.content_format,
            "content_length": details.content_length,
            "content_duration": details.content_duration,
            "availability": details.availability,
            "updated_at": datetime.now(timezone.utc),
        }

        result = await campaigns_collection.update_one(
            {"campaign_id": state.campaign_id, "influencer_id": state.influencer_id},
            {"$set": update_data},
        )
        print("Updated influencer details in database")
        if result.modified_count == 0:
            logger.warning(
                f"No document updated for influencer {state.influencer_id} in campaign {state.campaign_id}"
            )
        confirmation_msg = "Thanks for sharing your availability! We'll review and get back to you shortly."
        await Send_Insta_Message(
            message=confirmation_msg,
            recipient_id=state.thread_id,
        )
        print(f"Sent confirmation message to {state.thread_id}")
        state.reply = confirmation_msg
    except Exception as e:
        logger.exception(f"Error in Influencers Details Node: {e}")
        state.reply = "Thanks! We'll get back to you shortly."

    print("Exiting from Influencers Details Node")
    return state
