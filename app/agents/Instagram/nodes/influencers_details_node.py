from app.Schemas.instagram.negotiation_schema import (
    InfluencerDetailsInput,
    InstagramConversationState,
)
from app.db.connection import get_db
from app.config.credentials_config import config
from app.services.instagram.send_instagram_message import Send_Insta_Message
from datetime import datetime, timezone


async def influencers_details_node(
    state: InstagramConversationState, details: InfluencerDetailsInput
):
    try:
        db = get_db()
        collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )

        update_data = details.dict()
        update_data["updated_at"] = datetime.now(timezone.utc)

        await collection.update_one(
            {"campaign_id": state.campaign_id, "influencer_id": state.influencer_id},
            {"$set": update_data},
        )

        confirmation_msg = (
            "Thanks for sharing your details! We'll get back to you shortly."
        )
        await Send_Insta_Message(message=confirmation_msg, recipient_id=state.thread_id)
        state.final_reply = confirmation_msg

    except Exception as e:
        state.final_reply = "Thanks! We'll get back to you shortly."
    return state
