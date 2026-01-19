from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message


async def send_instagram_reply(state: InstagramConversationState):
    if not state.final_reply:
        return state

    await Send_Insta_Message(
        message=state.final_reply,
        recipient_id=state.thread_id,
    )
    return state
