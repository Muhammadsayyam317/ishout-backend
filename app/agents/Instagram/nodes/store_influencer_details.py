from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message
from app.db.connection import get_db
from app.config.credentials_config import config
from datetime import datetime, timezone


async def store_influencer_details(state: InstagramConversationState):
    print("Entering into Influencers Details")
    print("--------------------------------")
    print(state)
    print("--------------------------------")

    influencer_details = state.get("influencer_details")

    if not influencer_details:
        state["final_reply"] = "Please provide your campaign details."
        return state

    db = get_db()
    collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)

    update_data = influencer_details.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc)

    await collection.update_one(
        {
            "campaign_id": state.get("campaign_id"),
            "influencer_id": state.get("influencer_id"),
        },
        {"$set": update_data},
        upsert=True,
    )

    confirmation_msg = "Thanks for sharing your details! We'll get back to you shortly."
    await Send_Insta_Message(
        message=confirmation_msg,
        recipient_id=state.get("thread_id"),
    )

    state["final_reply"] = confirmation_msg
    print("Exiting from Influencers Details")
    return state
