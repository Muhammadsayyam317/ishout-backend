import logging
from app.models.whatsappconversation_model import ConversationState
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state: ConversationState):
    platform = state.get("platform")
    print(f"[Query_to_llm] Platform: {platform}")
    limit = state.get("number_of_influencers")
    print(f"[Query_to_llm] Limit: {limit}")
    country = state.get("country")
    print(f"[Query_to_llm] Country: {country}")
    category = state.get("category")
    print(f"[Query_to_llm] Category: {category}")

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
        return "iShout need these details before searching: " + ", ".join(missing)
    print(f"[Query_to_llm] Missing: {missing}")
    logging.info(f"[Query_to_llm] Missing: {missing}")

    influencers = find_influencers_for_whatsapp(
        category=category,
        platform=platform,
        number_of_influencers=limit,
        country=country,
    )
    print(f"[Query_to_llm] Influencers: {influencers}")
    logging.info(f"[Query_to_llm] Influencers: {influencers}")
    print("[Query_to_llm] No influencers found with these filters.")
    logging.info("[Query_to_llm] No influencers found with these filters.")
    if not influencers:
        return "No influencers found with these filters."

    response = f"I found {len(influencers)} influencer(s):\n\n"
    for i, inf in enumerate(influencers, 1):
        response += f"{i}. {inf}\n\n"
    return response
