from datetime import datetime, timezone
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    InfluencerDetails,
)
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def instauser_session(state: InstagramConversationState):
    """
    Store Instagram session info for dashboard.
    Extracts data from `state`.
    """
    try:
        db = get_db()
        collection = db.get_collection("instagram_sessions")

        influencer_details = InfluencerDetails(
            influencer_id=state.get("influencer_id"),
            campaign_id=state.get("campaign_id"),
            thread_id=state.get("thread_id"),
            last_message=state.get("last_message"),
            user_message=state.get("user_message"),
            history=state.get("history", []),
            pricing_rules=state.get("pricing_rules"),
            negotiation_status=state.get("negotiation_status"),
            next_action=state.get("next_action"),
            final_reply=state.get("final_reply"),
            final_rate=state.get("final_rate"),
            manual_negotiation_required=state.get("manual_negotiation_required"),
            last_updated=datetime.now(timezone.utc),
        )

        await collection.update_one(
            {"thread_id": state["thread_id"]}, {"$set": influencer_details}, upsert=True
        )
        print(f"Instagram user session updated for thread_id: {state['thread_id']}")
        return state

    except Exception as e:
        raise InternalServerErrorException(f"Error in instauser_session: {e}") from e
