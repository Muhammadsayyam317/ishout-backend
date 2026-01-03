from app.services.whatsapp.onboarding_message import send_whatsapp_message
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import AI_IDENTITY, SenderType


async def node_send_reply(state):
    print("Entering node_send_reply")
    try:
        reply = state.get("reply")
        sender_id = state.get("sender_id")
        print(f"Reply in node_send_reply: {reply}")
        if not sender_id:
            raise ValueError("sender_id missing in state")
        if reply and not state.get("reply_sent"):
            print(f"Sending reply to {sender_id}: {reply}")
            await send_whatsapp_message(sender_id, reply)
            print(f"Sending reply to {sender_id}: {reply}")
            await save_conversation_message(
                thread_id=sender_id,
                username=AI_IDENTITY["username"],
                sender=SenderType.AI.value,
                message=reply,
            )
            state["reply_sent"] = True
        return state
    except Exception as e:
        print(f"❌ Error in node_send_reply: {e}")
        state["reply_sent"] = True
        state["done"] = True
        print("Exiting node_send_reply with error")
        return state
