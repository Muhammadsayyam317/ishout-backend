from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)
from app.config.credentials_config import config
from app.db.connection import get_db


async def fetch_pricing_rules(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("Entering into Fetch Pricing Rules")
    db = get_db()
    collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)

    doc = await collection.find_one(
        {
            "campaign_id": state["campaign_id"],
            "influencer_id": state["influencer_id"],
        }
    )

    if not doc:
        state["pricingRules"] = {"minPrice": 0, "maxPrice": 0}
        return state

    state["pricingRules"] = {
        "minPrice": doc["min_price"],
        "maxPrice": doc["max_price"],
    }

    return state
