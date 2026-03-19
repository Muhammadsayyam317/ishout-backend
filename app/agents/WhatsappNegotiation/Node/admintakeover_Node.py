from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db
from bson import ObjectId


async def admin_takeover_node(state: WhatsappNegotiationState):
    thread_id = state.get("thread_id")
    if not thread_id:
        print("[admin_takeover_node] Missing thread_id")
        return state

    state["admin_takeover"] = True
    state["human_takeover"] = True
    state["agent_paused"] = True
    state["conversation_mode"] = "NEGOTIATION"
    state["negotiation_status"] = "manual_required"
    state["next_action"] = None

    influencer_id = state.get("influencer_id")
    if not influencer_id:
        print("[admin_takeover_node] Missing influencer_id; skip campaign_influencers update")
    else:
        try:
            db = get_db()
            collection = db.get_collection("campaign_influencers")
            await collection.update_one(
                {"_id": ObjectId(influencer_id)},
                {
                    "$set": {
                        "admin_takeover": state["admin_takeover"],
                        "human_takeover": state["human_takeover"],
                        "agent_paused": state["agent_paused"],
                        "conversation_mode": state["conversation_mode"],
                        "negotiation_status": state["negotiation_status"],
                        "next_action": state["next_action"],
                        "last_offered_price": state.get("last_offered_price"),
                    }
                },
            )
        except Exception as e:
            print(f"[admin_takeover_node] Mongo persistence failed: {e}")

    return state
