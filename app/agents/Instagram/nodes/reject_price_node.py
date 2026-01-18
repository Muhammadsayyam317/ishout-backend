from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.db.connection import get_db
from app.config.credentials_config import config
import logging

logger = logging.getLogger(__name__)


async def manual_negotiation_required(
    state: InstagramConversationState,
) -> InstagramConversationState:
    """
    Flags the influencer as 'Manual Negotiation Required' if they reject both min and max prices.
    """
    try:
        offered_price = getattr(state.analysis, "budget_amount", None)
        if offered_price is None:
            return state

        if offered_price < state.min_price or offered_price > state.max_price:
            db = get_db()
            campaigns_collection = db.get_collection(
                config.CAMPAIGN_INFLUENCERS_COLLECTION
            )

            result = await campaigns_collection.update_one(
                {
                    "campaign_id": state.campaign_id,
                    "influencer_id": state.influencer_id,
                },
                {
                    "$set": {
                        "manual_negotiation_required": True,
                        "negotiation_stage": "MANUAL",
                    }
                },
            )
            if result.modified_count == 0:
                raise Exception(
                    f"Failed to flag influencer {state.influencer_id} for manual negotiation in campaign {state.campaign_id}."
                )
            logger.info(
                f"Flagged influencer {state.influencer_id} for manual negotiation in campaign {state.campaign_id}."
            )

    except Exception as e:
        logger.exception(f"Error in manual_negotiation_required node: {e}")

    return state
