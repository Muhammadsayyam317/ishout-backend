from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


from app.db.connection import get_db
from bson import ObjectId


async def admin_takeover_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering admin_takeover_node")
    print("--------------------------------")

    thread_id = state.get("thread_id")
    if not thread_id:
        print(f"{Colors.RED}[admin_takeover_node] Missing thread_id")
        return state

    # Update state flags
    state["admin_takeover"] = True
    state["human_takeover"] = True
    state["agent_paused"] = True
    state["conversation_mode"] = "NEGOTIATION"
    state["negotiation_status"] = "manual_required"
    state["next_action"] = None

    # Persist to Mongo
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "admin_takeover": state["admin_takeover"],
                    "human_takeover": state["human_takeover"],
                    "agent_paused": state["agent_paused"],
                    "conversation_mode": state["conversation_mode"],
                    "negotiation_status": state["negotiation_status"],
                    "next_action": state["next_action"],
                }
            },
        )
    except Exception as e:
        print(f"[admin_takeover_node] Mongo persistence failed: {e}")

    print(
        f"{Colors.CYAN}[admin_takeover_node] Admin takeover triggered for thread {thread_id}"
    )
    print(f"{Colors.YELLOW}Exiting from admin_takeover_node")
    print("--------------------------------")
    return state
