from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.db.connection import get_db
from app.config.credentials_config import config
import logging

logger = logging.getLogger(__name__)


async def negotiation_succeeds(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("Enter into Negotiation Succeeds Node")
    try:
        if (
            state.analysis is None
            or getattr(state.analysis, "budget_amount", None) is None
        ):
            logger.warning(
                "No budget_amount found in state.analysis. Cannot mark negotiation as succeeded."
            )
            return state
        final_rate = state.analysis.budget_amount

        db = get_db()
        campaigns_collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )

        result = await campaigns_collection.update_one(
            {"campaign_id": state.campaign_id, "influencer_id": state.influencer_id},
            {
                "$set": {
                    "negotiation_stage": "CONFIRMED",
                    "final_rate": final_rate,
                    "manual_negotiation_required": False,
                }
            },
        )
        if result.modified_count == 0:
            raise Exception(
                f"Failed to mark negotiation as succeeded for influencer {state.influencer_id} in campaign {state.campaign_id}."
            )
        logger.info(
            f"Negotiation succeeded: Influencer {state.influencer_id} confirmed for campaign {state.campaign_id} at rate {final_rate}"
        )

    except Exception as e:
        logger.exception(f"Error in negotiation_succeeds node: {e}")

    print("Exiting from Negotiation Succeeds Node")
    return state
