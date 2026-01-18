from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message


async def send_instagram_reply(
    state: InstagramConversationState,
) -> InstagramConversationState:
    """
    Send the AI reply to Instagram.
    """
    print(f"Sending reply to {state.thread_id}: {state.reply.reply}")
    await Send_Insta_Message(
        message=state.reply.reply,
        recipient_id=state.thread_id,
    )
    return state
