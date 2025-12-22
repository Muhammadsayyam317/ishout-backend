from app.services.whatsapp.onboarding_Whatsapp_message import send_whatsapp_message


async def node_send_reply(state):
    print("Entering node_send_reply")
    try:
        reply = state.get("reply")
        sender_id = state.get("sender_id")
        if not sender_id:
            raise ValueError("sender_id missing in state")
        if reply and not state.get("reply_sent"):
            await send_whatsapp_message(sender_id, reply)
            state["reply_sent"] = True

        return state

    except Exception as e:
        print(f"❌ Error in node_send_reply: {e}")
        state["reply_sent"] = True
        state["done"] = True
        print("Exiting node_send_reply with error")
        return state
