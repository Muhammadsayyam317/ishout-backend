from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(payload: dict) -> str:
    initial_state: InstagramConversationState = {
        "thread_id": payload["thread_id"],
        "convoId": payload.get("convoId", ""),
        "user_message": payload["message"],
        "lastMessage": payload.get("message", ""),
        "influencer_id": payload.get("influencer_id", ""),
        "campaign_id": payload.get("campaign_id", ""),
    }

    result = await instagram_graph.ainvoke(initial_state)
    print("Final LangGraph state:", result)
    print("Final LangGraph state keys:", result.keys())
    print("Final LangGraph state final_reply:", result.get("final_reply"))
    final_reply = result.get("final_reply")
    if not final_reply:
        return "Thanks for your message! We'll get back to you shortly."
    return final_reply
