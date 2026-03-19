from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db
from bson import ObjectId
from app.config.credentials_config import config


async def reject_negotiation_node(state: WhatsappNegotiationState):
    state["negotiation_status"] = "rejected"
    state["negotiation_completed"] = True
    state["conversation_mode"] = "HUMAN_TAKEOVER"
    state["human_takeover"] = True
    # Pause the negotiation agent so further messages don't re-trigger the flow.
    state["agent_paused"] = True
    state["final_reply"] = (
        "Thanks for your time! We understand this isn’t a fit at the moment. "
        "We’ll keep you in mind for future campaigns."
    )
    state["next_action"] = None

    # Append the final reply to in-memory history so negotiation dashboards
    # see the last AI message in the conversation thread.
    state.setdefault("history", []).append(
        {
            "sender_type": "AI",
            "message": state["final_reply"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    influencer_id = state.get("influencer_id")
    if not influencer_id:
        print("[reject_negotiation_node] Missing influencer_id; skip campaign_influencers update")
    else:
        try:
            db = get_db()
            collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)
            await collection.update_one(
                {"_id": ObjectId(influencer_id)},
                {
                    "$set": {
                        "negotiation_status": state["negotiation_status"],
                        "negotiation_completed": state.get("negotiation_completed"),
                        "conversation_mode": state.get("conversation_mode"),
                        "human_takeover": state.get("human_takeover"),
                        "agent_paused": state.get("agent_paused"),
                        "final_reply": state["final_reply"],
                        "next_action": state["next_action"],
                        "last_offered_price": state.get("last_offered_price"),
                    }
                },
            )
        except Exception as e:
            print(f"[reject_negotiation_node] Mongo persistence failed: {e}")

    return state
