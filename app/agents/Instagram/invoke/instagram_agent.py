from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(payload: dict) -> str:
    psid = payload["thread_id"]
    initial_state = InstagramConversationState(
        thread_id=psid,
        user_message=payload["message"],
    )
    print(
        f"Initial state: {{'thread_id': {initial_state.thread_id}, 'user_message': {initial_state.user_message[:50]}}}"
    )
    result = await instagram_graph.ainvoke(initial_state)
    print(f"Result: {result}")
    final_reply = result.get("final_reply")
    print(f"Final reply: {final_reply}")
    if not final_reply:
        final_reply = "Thanks for your message! We'll get back to you shortly."
    return final_reply
