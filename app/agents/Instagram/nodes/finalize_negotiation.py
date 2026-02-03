from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)
from app.db.connection import get_db


async def finalize_negotiation(state: InstagramConversationState):
    print("Entering Node: Finalize Negotiation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")

    db = get_db()
    collection = db.get_collection("campaign_influencers")

    status = state["negotiation_status"].upper()  # Normalize for consistency

    if status == "CONFIRMED":
        final_rate = state.get("final_rate") or state["influencer_response"].get("rate")
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
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE

    elif status == "REJECTED":
        await collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {"$set": {"negotiation_stage": "REJECTED"}},
        )
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE

    elif status == "MANUAL_REQUIRED":
        await collection.update_one(
            {
                "campaign_id": state["campaign_id"],
                "influencer_id": state["influencer_id"],
            },
            {
                "$set": {
                    "negotiation_stage": "MANUAL_REQUIRED",
                    "manual_negotiation_required": True,
                }
            },
        )
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION

    else:
        # Fallback for unexpected statuses
        print(f"Warning: Unexpected negotiation_status '{state['negotiation_status']}'")
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE

    print("Exiting Node: Finalize Negotiation")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
