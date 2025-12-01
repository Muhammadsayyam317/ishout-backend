import logging
from app.agents.nodes.graph import missing_fields
from app.models.whatsappconversation_model import ConversationState
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state: ConversationState):
    platform = state.get("platform")
    limit = state.get("number_of_influencers")
    country = state.get("country")
    budget = state.get("budget")
    category = state.get("category")

    missing = missing_fields(state)
    if missing:
        return (
            "I need these details before searching: "
            + ", ".join(missing)
            + ". Please reply with them."
        )

    query_parts = [p for p in [category, platform, country] if p]
    if budget:
        query_parts.append(f"budget:{budget}")
    query = " ".join(query_parts)

    influencers = await find_influencers_for_whatsapp(
        query=query,
        platform=platform,
        limit=limit,
        country=country,
        budget=budget,
        influencer_limit=limit,
    )

    if not influencers:
        return "No influencers found with these filters."

    response = f"I found {len(influencers)} influencer(s):\n\n"
    for i, inf in enumerate(influencers, 1):
        username = inf.get("username") or inf.get("name", "Unknown")
        response += f"{i}. @{username} ({platform})\n"
    return response
