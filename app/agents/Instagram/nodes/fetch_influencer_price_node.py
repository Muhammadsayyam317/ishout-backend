from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.config.credentials_config import config
from app.db.connection import get_db


async def fetch_pricing_rules(state: InstagramConversationState):
    print("Entering into Node Fetch Pricing Rules")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    db = get_db()
    collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)
    doc = await collection.find_one(
        {
            "campaign_id": state["campaign_id"],
            "influencer_id": state["influencer_id"],
        }
    )

    state["pricing_rules"] = {
        "minPrice": doc.get("min_price", 0) if doc else 0,
        "maxPrice": doc.get("max_price", 0) if doc else 0,
    }
    print("Exiting from Node Fetch Pricing Rules")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
