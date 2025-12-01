import logging
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(state):
    try:
        # Use accumulated state to build a human readable query for the influencer DB/LLM
        platform = state.get("platform")
        limit = state.get("number_of_influencers")
        country = state.get("country")
        budget = state.get("budget")
        category = state.get("category")

        missing = []
        if not platform:
            missing.append("platform (e.g. Instagram, TikTok, YouTube)")
        if not country:
            missing.append("country (e.g. UAE, Kuwait, Saudi Arabia)")
        if limit is None:
            missing.append("number of influencers")

        if missing:
            return (
                "I need these details before searching: "
                + ", ".join(missing)
                + ".\nPlease reply with them, for example: "
                "'Platform is Instagram, category is fashion, country is UAE, and I need 4 influencers.'"
            )

        # Build a clear query string for the influencer search
        parts = []
        if category:
            parts.append(category)
        if platform:
            parts.append(platform)
        if country:
            parts.append(country)
        if budget:
            parts.append(f"budget {budget}")
        query = " ".join(parts) if parts else (state.get("user_message") or "")

        search_limit = int(limit) if limit else 5

        influencers = await find_influencers_for_whatsapp(
            query=query,
            platform=platform,
            limit=search_limit,
            country=country,
            budget=budget,
            influencer_limit=search_limit,
        )

        if not influencers:
            return (
                "I couldn't find any influencers matching your request. "
                "Could you try rephrasing your query? For example:\n"
                "1. 'Find 2-6 beauty influencers on Instagram'\n"
                "2. 'Show me 2-6 fitness influencers on TikTok in UAE'\n"
            )

        response = f"I found {len(influencers)} influencer(s) for you:\n\n"
        for i, influencer in enumerate(influencers[:search_limit], 1):
            username = influencer.get("username", influencer.get("name", "Unknown"))
            followers = influencer.get(
                "followers", influencer.get("follower_count", "N/A")
            )
            platform_name = influencer.get("platform", platform)

            response += f"{i}. @{username} ({platform_name})\n"
            if followers:
                response += f"   Followers: {followers}\n"
            response += "\n"

        return response

    except Exception as e:
        logging.error(f"Error handling request: {e}", exc_info=True)
        return (
            "An error occurred while processing your request. Please try again later."
        )
