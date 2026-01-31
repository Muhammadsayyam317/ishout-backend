from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from app.db.connection import get_db
from app.config.credentials_config import config
import logging

logger = logging.getLogger(__name__)


async def finalize_negotiation(state: InstagramConversationState):
    print("Entering into Node Finalize Negotiation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    db = get_db()
    collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)

    if state["negotiation_status"] == "agreed":
        final_rate = state["influencer_response"].get("rate")
        await collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {
                "$set": {
                    "negotiation_stage": "CONFIRMED",
                    "final_rate": final_rate,
                    "manual_negotiation_required": False,
                }
            },
        )
        logger.info(f"Negotiation succeeded: {state['influencer_id']}")
    elif state["negotiation_status"] == "rejected":
        await collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {"$set": {"negotiation_stage": "REJECTED"}},
        )
        logger.info(f"Negotiation rejected: {state['influencer_id']}")

    print("Exiting from Node Finalize Negotiation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
