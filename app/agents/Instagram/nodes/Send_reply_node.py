from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message


async def send_instagram_reply(
    state: InstagramConversationState,
) -> InstagramConversationState:

    if not state.reply:
        print("Empty reply in Send Reply Node")
        return state
    print(f"Sending reply to {state.thread_id}: {state.reply} in Send Reply Node")
    await Send_Insta_Message(
        message=state.reply,
        recipient_id=state.thread_id,
    )
    print("Exiting from Send Reply Node")
    return state
