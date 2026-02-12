from datetime import datetime, timezone
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db


async def admin_takeover_node(state: WhatsappNegotiationState):
    influencer_id = state.get("influencer_id", "Unknown")
    thread_id = state.get("thread_id")
    if not thread_id:
        print("[admin_takeover_node] Missing thread_id, cannot update DB")
        return state

    print(
        f"[admin_takeover_node] Admin takeover triggered for influencer {influencer_id}"
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
    except Exception as e:
        print(f"[admin_takeover_node] Error updating DB: {e}")

    return state
