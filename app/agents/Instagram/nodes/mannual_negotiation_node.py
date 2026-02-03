from datetime import datetime, timezone
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.db.connection import get_db
import logging

logger = logging.getLogger(__name__)


async def manual_negotiation_required(state: InstagramConversationState):
    db = get_db()
    collection = db.get_collection("campaign_influencers")

    await collection.update_one(
        {
            "campaign_id": state["campaign_id"],
            "influencer_id": state["influencer_id"],
        },
        {
            "$set": {
                "negotiation_status": "MANUAL_REQUIRED",
                "requested_rate": state["influencer_response"]["rate"],
                "system_min": state["pricing_rules"]["minPrice"],
                "system_max": state["pricing_rules"]["maxPrice"],
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    return state
