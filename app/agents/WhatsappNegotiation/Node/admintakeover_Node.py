from datetime import datetime, timezone
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.printcolors import Colors


async def admin_takeover_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering admin_takeover_node")
    print("--------------------------------")

    thread_id = state.get("thread_id")
    _id = state.get("_id")

    if not thread_id:
        print(f"{Colors.RED}[admin_takeover_node] Missing thread_id, cannot update DB")
        return state

    print(
        f"{Colors.CYAN}[admin_takeover_node] Admin takeover triggered for influencer {_id}"
    )

    db = get_db()
    collection = db.get_collection("negotiation_agent_controls")

    try:
        await collection.update_one(
            {"thread_id": thread_id},
            {
                "$set": {
                    "human_takeover": True,
                    "agent_paused": True,
                    "conversation_mode": "NEGOTIATION",
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

        state["admin_takeover"] = True
        state["negotiation_status"] = "manual_required"
        state["next_action"] = None
        print(
            f"{Colors.CYAN}[admin_takeover_node] DB updated successfully for thread {thread_id}"
        )

    except Exception as e:
        print(f"{Colors.RED}[admin_takeover_node] Error updating DB: {e}")
        raise InternalServerErrorException(message=f"Admin takeover failed: {e}")

    print(f"{Colors.YELLOW}Exiting from admin_takeover_node")
    print("--------------------------------")
    return state
