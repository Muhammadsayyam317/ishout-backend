from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.config.credentials_config import config
from app.db.connection import get_db
import logging

logger = logging.getLogger(__name__)


async def manual_negotiation_required(state: InstagramConversationState):
    print("Entering into Node Manual Negotiation Required")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    offered_price = state["influencer_response"].get("rate")
    min_price = state["pricing_rules"].get("minPrice", 0)
    max_price = state["pricing_rules"].get("maxPrice", float("inf"))

    if offered_price is None or min_price <= offered_price <= max_price:
        return state

    db = get_db()
    collection = db.get_collection("campaign_influencers")
    await collection.update_one(
        {"campaign_id": state["campaign_id"], "influencer_id": state["influencer_id"]},
        {"$set": {"manual_negotiation_required": True, "negotiation_stage": "MANUAL"}},
    )
    logger.info(f"Flagged manual negotiation for influencer {state['influencer_id']}")
    print("Exiting from Node Manual Negotiation Required")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
