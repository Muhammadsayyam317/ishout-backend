from app.model.whatsappconversation import AgentControl
from app.db.connection import get_db


async def node_check_agent_control(state):
    db = get_db()
    control: AgentControl = await db.get_collection("agent_controls").find_one(
        {"thread_id": state["sender_id"]}
    )

    if control:
        # Human takeover
        if control.get("human_takeover"):
            state["blocked"] = True
            state["block_reason"] = "HUMAN_TAKEOVER"
            state["reply"] = None
            state["reply_sent"] = True
            state["done"] = True
            return state

        # ⏸ Agent paused → send auto message
        if control.get("agent_paused"):
            state["blocked"] = True
            state["block_reason"] = "AGENT_PAUSED"
            state["reply"] = (
                "⏸️ Our agent is currently paused.\n" "A human will respond you shortly."
            )
            state["reply_sent"] = False
            state["done"] = False
            return state

    state["blocked"] = False
    return state
