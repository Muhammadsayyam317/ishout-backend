from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(payload: dict) -> str:
    state = InstagramConversationState(
        thread_id=payload["thread_id"], user_message=payload["message"]
    )
    state = await instagram_graph.ainvoke(state)

    if not state.final_reply:
        return "Thanks for your message! We'll get back to you shortly."
    return state.final_reply
