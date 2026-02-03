from app.agents.Whatsapp.nodes.state import (
    cleanup_old_checkpoints,
    increment_conversation_round,
)
from app.agents.Whatsapp.state.reset_state import reset_user_state
from app.services.whatsapp.onboarding_message import send_whatsapp_message
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType
from app.db.connection import get_db


async def node_send_reply(state):
    print("Entering into node_send_reply")
    print("--------------------------------")
    sender_id = state.get("sender_id")
    reply = state.get("reply")
    if not sender_id or not reply:
        return state
    db = get_db()
    control = await db.get_collection("agent_controls").find_one(
        {"thread_id": sender_id}
    )
    if control and control.get("human_takeover"):
        state["reply_sent"] = True
        return state
    await send_whatsapp_message(sender_id, reply)
    await save_conversation_message(
        thread_id=sender_id,
        sender=SenderType.AI.value,
        message=reply,
    )
    state["reply_sent"] = True
    if state.get("reset_after_reply"):
        print("♻️ Resetting full conversation state")
        # Increment conversation round
        new_round = await increment_conversation_round(sender_id)
        print("New round: ", new_round)
        print("--------------------------------")
        # Reset Mongo session
        await reset_user_state(sender_id)
        print("Reset user state")
        print("--------------------------------")
        # Cleanup Redis checkpoints
        await cleanup_old_checkpoints(thread_id=sender_id, keep_round=new_round)
        print("Cleanup old checkpoints")
        print("--------------------------------")
        state.clear()
        print("Clear state")
        print("--------------------------------")
        state["sender_id"] = sender_id
        print("Set sender id")
        print("--------------------------------")
    print("Exiting from node_send_reply")
    print("--------------------------------")
    return state
