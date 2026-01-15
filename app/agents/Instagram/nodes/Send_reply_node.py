from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message


async def send_instagram_reply(state: InstagramConversationState):
    print(f"Sending reply to {state.thread_id}: {state.final_reply}")
    await Send_Insta_Message(
        message=state.final_reply,
        recipient_id=state.thread_id,
    )
    print(f"Reply sent to {state.thread_id}: {state.final_reply}")
    state.final_reply = state.final_reply
    print(f"Reply sent to {state.thread_id}: {state.final_reply}")
    return state
