from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(payload: dict) -> str:
    initial_state = InstagramConversationState(
        thread_id=payload["thread_id"],
        user_message=payload["message"],
        influencer_id=payload.get("influencer_id"),
        campaign_id=payload.get("campaign_id"),
        influencer_details=payload.get("influencer_details"),
    )

    result = await instagram_graph.ainvoke(initial_state)
    if not result.final_reply:
        return "Thanks for your message! We'll get back to you shortly."
    return result.final_reply
