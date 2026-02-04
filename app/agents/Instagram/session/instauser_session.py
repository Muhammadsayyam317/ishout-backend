from datetime import datetime, timezone
from app.Schemas.instagram.negotiation_schema import (
    InfluencerDetails,
    InstagramConversationState,
)
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def instauser_session(state: InstagramConversationState):
    try:
        db = get_db()
        collection = db.get_collection("instagram_sessions")

        requested_rate = state.get("influencer_response", {}).get("rate", 0)
        min_price = state.get("pricing_rules", {}).get("minPrice", 0)
        max_price = state.get("pricing_rules", {}).get("maxPrice", 0)
        final_rate = state.get("final_rate")

        if requested_rate and final_rate is None:
            final_rate = requested_rate
            agreed_rate = "manual"
            negotiation_status = "manual required"
            human_escalation_required = True
        else:
            agreed_rate = (
                "system" if state.get("negotiation_status") == "confirmed" else "manual"
            )
            negotiation_status = state.get("negotiation_status", "manual required")
            human_escalation_required = negotiation_status == "manual required"

        influencer_details: InfluencerDetails = {
            "requested_rate": requested_rate,
            "min_price": min_price,
            "max_price": max_price,
            "final_rate": final_rate,
            "last_updated": datetime.now(timezone.utc),
            "agreed_rate": agreed_rate,
            "negotiation_status": negotiation_status,
            "human_escalation_required": human_escalation_required,
        }

        await collection.update_one(
            {"thread_id": state["thread_id"]},
            {"$set": influencer_details},
            upsert=True,
        )

        print(f"Instagram user session updated for thread_id: {state['thread_id']}")
        return state

    except Exception as e:
        raise InternalServerErrorException(f"Error in instauser_session: {e}") from e
