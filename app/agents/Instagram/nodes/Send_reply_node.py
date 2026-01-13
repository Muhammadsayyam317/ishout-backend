from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram import send_instagram_message


async def send_instagram_reply(state: InstagramConversationState):
    print(f"Sending reply to {state.thread_id}: {state.ai_draft}")
    await send_instagram_message(
        recipient_id=state.thread_id,
        text=state.ai_draft,
    )

    state.final_reply = state.ai_draft
    return state
