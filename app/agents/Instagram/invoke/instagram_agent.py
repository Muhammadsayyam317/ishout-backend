from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.graph.instagram_graph import instagram_graph


async def instagram_negotiation_agent(
    payload: InstagramConversationState,
) -> GenerateReplyOutput:
    result = await instagram_graph.ainvoke(payload)
    print(f"Result: {result}")
    return result.reply
