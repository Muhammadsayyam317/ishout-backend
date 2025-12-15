from app.services.whatsapp.onboarding_Whatsapp_message import send_whatsapp_message


async def node_send_reply(state):
    reply = state.get("reply")

    if reply and not state.get("reply_sent"):
        await send_whatsapp_message(
            state["sender_id"],
            reply,
        )
        state["reply_sent"] = True

    return state
