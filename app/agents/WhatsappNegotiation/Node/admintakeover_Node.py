from datetime import datetime, timezone
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.printcolors import Colors


async def admin_takeover_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into admin_takeover_node")
    print("--------------------------------")
    _id = state.get("_id")
    thread_id = state.get("thread_id")
    if not thread_id:
        print("[admin_takeover_node] Missing thread_id, cannot update DB")
        return state
    print(
        f"[admin_takeover_node] Admin takeover triggered for campaign influencer {_id}"
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
                    "updated_at": datetime.now(timezone.utc),
                    "conversation_mode": "NEGOTIATION",
                }
            },
            upsert=True,
        )
        state["admin_takeover"] = True
        print(f"[admin_takeover_node] DB updated successfully for thread {thread_id}")
        print(f"{Colors.CYAN} Exiting from admin_takeover_node")
        print("--------------------------------")
    except Exception as e:
        print(f"{Colors.RED}Error updating DB: {e}")
        print("--------------------------------")
        raise InternalServerErrorException(message=f"Admin takeover failed: {e}")
    return state
