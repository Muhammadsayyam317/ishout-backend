from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    SenderType,
)
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(payload: dict) -> str:
    psid = payload["thread_id"]
    initial_state = InstagramConversationState(
        thread_id=psid,
        user_message=payload["message"],
        sender_type=payload["sender_type"],
    )
    print(
        f"Initial state: {{'thread_id': {initial_state.thread_id}, 'user_message': {initial_state.user_message[:50]}}}"
    )
    if initial_state.sender_type == SenderType.AI:
        print("🛑 Message from admin, skipping agent processing")
        return None

    result = await instagram_graph.ainvoke(initial_state)
    reply = result.get("reply")
    print(f"Reply: {reply}")
    if not reply.reply:
        reply.reply = "Thanks for your message! We'll get back to you shortly."
    return reply
