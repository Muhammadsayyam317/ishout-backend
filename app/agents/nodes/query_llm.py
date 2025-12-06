from app.models.whatsappconversation_model import ConversationState
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state: ConversationState):
    platform = state.get("platform") or []
    limit = state.get("limit")
    country = state.get("country") or []
    category = state.get("category") or []
    followers = state.get("followers") or []
    missing = []

    # Check if arrays are empty
    if not platform or (isinstance(platform, list) and len(platform) == 0):
        missing.append("platform (e.g. Instagram, TikTok, YouTube)")
    if not country or (isinstance(country, list) and len(country) == 0):
        missing.append("country (e.g. UAE, Kuwait, Saudi Arabia)")
    if not limit:
        missing.append("Number of influencers (e.g. 10, 20, 30)")
    if not category or (isinstance(category, list) and len(category) == 0):
        missing.append("Category (e.g. fashion, beauty, tech)")
    if not followers or (isinstance(followers, list) and len(followers) == 0):
        missing.append("Followers count (e.g. 10k, 2M, 3000K)")

    if missing:
        return "iShout need these details before searching: " + ", ".join(missing)

    influencers = find_influencers_for_whatsapp(
        category=category,
        platform=platform,
        limit=limit,
        country=country,
        followers=followers,
    )

    if not influencers:
        return "No influencers found with these filters."
    response = f"I found {len(influencers)} influencer(s):\n\n"
    for i, inf in enumerate(influencers, 1):
        response += f"{i}. {inf}\n\n"
    return response
