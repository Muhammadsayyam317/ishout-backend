import logging
from app.models.whatsappconversation_model import ConversationState
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state: ConversationState):
    platform = state.get("platform")
    limit = state.get("number_of_influencers")
    country = state.get("country")
    budget = state.get("budget")
    category = state.get("category")
    logging.info(f"[Query_to_llm] Platform: {platform}")
    logging.info(f"[Query_to_llm] Limit: {limit}")
    logging.info(f"[Query_to_llm] Country: {country}")
    logging.info(f"[Query_to_llm] Budget: {budget}")
    logging.info(f"[Query_to_llm] Category: {category}")

    missing = []
    if not platform:
        missing.append("platform (e.g. Instagram, TikTok, YouTube)")
    if not country:
        missing.append("country (e.g. UAE, Kuwait, Saudi Arabia)")
    if not limit:
        missing.append("number of influencers")
    if not category:
        missing.append("category (e.g. fashion, beauty, tech)")

    if missing:
        return (
            "I need these details before searching: "
            + ", ".join(missing)
            + ". Please reply with them."
        )
    logging.info(f"[Query_to_llm] Missing: {missing}")

    query_parts = [p for p in [category, platform, country] if p]
    if budget:
        query_parts.append(f"budget:{budget}")
    query = " ".join(query_parts)
    logging.info(f"[Query_to_llm] Query: {query}")

    influencers = await find_influencers_for_whatsapp(
        query=query,
        platform=platform,
        limit=limit,
        country=country,
        budget=budget,
        influencer_limit=limit,
    )
    logging.info(f"[Query_to_llm] Influencers: {influencers}")

    if not influencers:
        return "No influencers found with these filters."

    response = f"I found {len(influencers)} influencer(s):\n\n"
    for i, inf in enumerate(influencers, 1):
        username = inf.get("username") or inf.get("name", "Unknown")
        response += f"{i}. @{username} ({platform})\n"
    return response
