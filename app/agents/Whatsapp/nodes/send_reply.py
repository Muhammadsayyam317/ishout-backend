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
    sender_id = state.get("sender_id")
    reply = state.get("reply")

    if not sender_id or not reply:
        return state
    db = get_db()
    control = await db.get_collection("agent_controls").find_one(
        {"thread_id": sender_id}
    )
    if control and control.get("human_takeover"):
        print("⛔ AI blocked due to human takeover")
        state["reply_sent"] = True
        return state
    await send_whatsapp_message(sender_id, reply)
    print(f"Reply sent to {sender_id}: {reply}")
    await save_conversation_message(
        thread_id=sender_id,
        sender=SenderType.AI.value,
        message=reply,
    )
    print(f"Reply saved to {sender_id}: {reply}")
    state["reply_sent"] = True
    print(f"Reply sent: {state['reply_sent']} State: {state}")
    # RESET FLOW
    if state.get("reset_after_reply"):
        print("♻️ Resetting full conversation state")
        # Increment conversation round
        new_round = await increment_conversation_round(sender_id)
        # Reset Mongo session
        await reset_user_state(sender_id)
        # Cleanup Redis checkpoints
        await cleanup_old_checkpoints(thread_id=sender_id, keep_round=new_round)
        # Minimal state preservation
        state.clear()
        state["sender_id"] = sender_id
    return state
