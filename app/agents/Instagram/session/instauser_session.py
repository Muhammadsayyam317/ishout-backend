from datetime import datetime, timezone
from app.Schemas.instagram.negotiation_schema import (
    InfluencerDetails,
    InstagramConversationState,
)
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def instauser_session(state: InstagramConversationState):
    print("Entering Instagram User Session")
    print("--------------------------------")
    print("State: ", state)
    print("--------------------------------")
    try:
        db = get_db()
        session_collection = db.get_collection("instagram_sessions")
        campaign_collection = db.get_collection("campaign_influencers")

        campaign_doc = await campaign_collection.find_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            }
        )

        requested_rate = state.get("influencer_response", {}).get("rate", 0)
        min_price = state.get("pricing_rules", {}).get("minPrice", 0)
        max_price = state.get("pricing_rules", {}).get("maxPrice", 0)
        final_rate = state.get("final_rate")

        if campaign_doc:
            if requested_rate is not None and final_rate is None:
                final_rate = requested_rate

            agreed_rate = "system" if min_price <= final_rate <= max_price else "manual"
            negotiation_status = (
                "confirmed" if agreed_rate == "system" else "manual required"
            )
            human_escalation_required = negotiation_status == "manual required"

        else:
            final_rate = requested_rate or None
            agreed_rate = "manual"
            negotiation_status = "manual required"
            human_escalation_required = True

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

        # Save influencer session
        await session_collection.update_one(
            {"thread_id": state["thread_id"]},
            {"$set": influencer_details},
            upsert=True,
        )

        # Optionally update campaign DB only if influencer exists
        if campaign_doc:
            await campaign_collection.update_one(
                {
                    "campaign_id": state["campaign_id"],
                    "influencer_id": state["influencer_id"],
                },
                {
                    "$set": {
                        "final_rate": final_rate,
                        "negotiation_status": negotiation_status,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )

        print(f"Instagram user session updated for thread_id: {state['thread_id']}")
        print("--------------------------------")
        print("State: ", state)
        print("--------------------------------")
        return state

    except Exception as e:
        raise InternalServerErrorException(f"Error in instauser_session: {e}") from e
