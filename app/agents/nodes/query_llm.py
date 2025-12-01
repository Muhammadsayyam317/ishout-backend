import logging
from app.models.whatsappconversation_model import ConversationState
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state: ConversationState):
    platform = state.get("platform")
    logging.info(f"[Query_to_llm] Platform: {platform}")
    limit = state.get("number_of_influencers")
    logging.info(f"[Query_to_llm] Limit: {limit}")
    country = state.get("country")
    logging.info(f"[Query_to_llm] Country: {country}")
    category = state.get("category")
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
            "iShout need these details before searching: "
            + ", ".join(missing)
            + ". Please reply with them."
        )
    logging.info(f"[Query_to_llm] Missing: {missing}")
    query_parts = [p for p in [category, platform, country] if p]
    query = " ".join(query_parts)

    influencers = find_influencers_for_whatsapp(
        query=query,
        platform=platform,
        number_of_influencers=limit,
        country=country,
    )
    logging.info(f"[Query_to_llm] Influencers: {influencers}")

    if not influencers:
        return "No influencers found with these filters."

    response = f"I found {len(influencers)} influencer(s):\n\n"
    for i, inf in enumerate(influencers, 1):
        username = inf.get("username") or inf.get("name", "Unknown")
        response += f"{i}. @{username} ({platform})\n"
    return response
