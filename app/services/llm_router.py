import logging
import re
from app.services.message_classification import route_message_request
from app.agents.whatsapp_agent import find_influencers_for_whatsapp


async def llm_router(user_message: str, sender_id: str):
    try:
        classify_message, is_first = await route_message_request(
            user_message, sender_id
        )
        intent = classify_message.request_type

        if is_first and intent != "find_influencers":
            return "Hello! How may I help you to find influencers?"

        # If not about finding influencers (and not first message), return helpful message
        if intent != "find_influencers":
            return "I'm here to help you find influencers. Could you please tell me what kind of influencers you're looking for? For example: 'Find 10 beauty influencers on Instagram' or 'Show me fitness influencers on TikTok'."

        # If about finding influencers, use embedding service
        if intent == "find_influencers":
            platform = _extract_platform(user_message)
            limit = _extract_limit(user_message)

            query = (
                classify_message.description
                if hasattr(classify_message, "description")
                and classify_message.description
                else user_message
            )

            influencers = await find_influencers_for_whatsapp(
                query=query, platform=platform, limit=limit
            )

            if not influencers:
                return "I couldn't find any influencers matching your request. Could you try rephrasing your query? For example: 'Find 10 beauty influencers on Instagram' or 'Show me fitness influencers on TikTok'."

            # Format the response
            response = f"I found {len(influencers)} influencer(s) for you:\n\n"
            for i, influencer in enumerate(influencers[:limit], 1):
                username = influencer.get("username", influencer.get("name", "Unknown"))
                followers = influencer.get(
                    "followers", influencer.get("follower_count", "N/A")
                )
                bio = influencer.get("bio", influencer.get("description", ""))
                platform_name = influencer.get("platform", platform)

                response += f"{i}. @{username} ({platform_name})\n"
                if followers:
                    response += f"   Followers: {followers}\n"
                if bio:
                    bio_short = bio[:100] + "..." if len(bio) > 100 else bio
                    response += f"   Bio: {bio_short}\n"
                response += "\n"

            return response

        return "I'm unable to process that request. Can you provide more details?"

    except Exception as e:
        logging.error(f"Error handling request: {e}", exc_info=True)
        return (
            "An error occurred while processing your request. Please try again later."
        )


def _extract_platform(message: str) -> str:
    message_lower = message.lower()
    if "instagram" in message_lower or "insta" in message_lower:
        return "instagram"
    elif "tiktok" in message_lower or "tik tok" in message_lower:
        return "tiktok"
    elif "youtube" in message_lower or "yt" in message_lower:
        return "youtube"
    else:
        return "instagram"


def _extract_limit(message: str) -> int:
    numbers = re.findall(r"\d+", message)
    if numbers:
        try:
            limit = int(numbers[0])
            return min(limit, 20)
        except ValueError:
            pass
    return 5
