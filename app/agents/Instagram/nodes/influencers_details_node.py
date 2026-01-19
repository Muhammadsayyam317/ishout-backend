from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message
from app.db.connection import get_db
from app.config.credentials_config import config
from datetime import datetime, timezone


async def influencers_details_node(state: InstagramConversationState):
    if not state.influencer_details:
        state.final_reply = "Please provide your campaign details."
        return state

    details = state.influencer_details
    db = get_db()
    collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)
    update_data = details.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc)

    await collection.update_one(
        {"campaign_id": state.campaign_id, "influencer_id": state.influencer_id},
        {"$set": update_data},
    )

    confirmation_msg = "Thanks for sharing your details! We'll get back to you shortly."
    await Send_Insta_Message(message=confirmation_msg, recipient_id=state.thread_id)
    state.final_reply = confirmation_msg

    return state
