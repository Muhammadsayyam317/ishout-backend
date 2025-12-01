import logging
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp
from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import (
    extract_budget,
    extract_country,
    extract_limit,
    extract_platform,
)


async def Query_to_llm(state: ConversationState):
    """
    Handle 'find_influencers' intent using fields already extracted into state.
    - Read platform / number_of_influencers / country / budget from state.
    - If any key fields are missing, ask the user for them.
    - Otherwise, query the influencer store and format a response.
    """
    try:
        user_message = state.get("user_message") or ""

        # Prefer values already stored in state, fall back to extracting from current message
        platform = state.get("platform") or extract_platform(user_message)
        # IMPORTANT: preserve existing number_of_influencers if new message doesn't contain a number
        limit = state.get("number_of_influencers")
        if limit is None:
            limit = extract_limit(user_message)
        country = state.get("country") or extract_country(user_message)
        budget = state.get("budget") or extract_budget(user_message)

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
                "'Platform is Instagram, category is fashion, country is UAE, "
                "and I need 4 influencers.'"
            )

        search_limit = limit or 5

        influencers = await find_influencers_for_whatsapp(
            query=user_message,
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
