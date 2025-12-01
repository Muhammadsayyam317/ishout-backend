import logging
import re
from app.agents.nodes.message_classification import message_classification
from app.tools.whatsapp_influencer import find_influencers_for_whatsapp


async def Query_to_llm(user_message: str):
    try:
        classify_message = await message_classification(user_message)
        if classify_message.intent == "find_influencers":
            platform = extract_platform(user_message)
            limit = extract_limit(user_message)
            country = extract_country(user_message)
            budget = extract_budget(user_message)
            influencer_limit = extract_influencer_limit(user_message)

            query = (
                classify_message.description
                if hasattr(classify_message, "description")
                and classify_message.description
                else user_message
            )

            influencers = await find_influencers_for_whatsapp(
                query=query,
                platform=platform,
                limit=limit,
                country=country,
                budget=budget,
                influencer_limit=influencer_limit,
            )

            if not influencers:
                return "I couldn't find any influencers matching your request. Could you try rephrasing your query? For example: 'Find 2-6 beauty influencers on Instagram' or 'Show me 2-6 fitness influencers on TikTok at $1000 budget in UAE'."

            # Format the response
            response = f"I found {len(influencers)} influencer(s) for you:\n\n"
            for i, influencer in enumerate(influencers[:limit], 1):
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

        return "I'm unable to process that request. Can you provide more details?"

    except Exception as e:
        logging.error(f"Error handling request: {e}", exc_info=True)
        return (
            "An error occurred while processing your request. Please try again later."
        )


def extract_platform(message: str) -> str:
    message_lower = message.lower()
    if "instagram" in message_lower or "insta" in message_lower:
        return "instagram"
    elif "tiktok" in message_lower or "tik tok" in message_lower:
        return "tiktok"
    elif "youtube" in message_lower or "yt" in message_lower:
        return "youtube"
    else:
        return "instagram"


def extract_limit(message: str) -> int:
    numbers = re.findall(r"\d+", message)
    if numbers:
        try:
            limit = int(numbers[0])
            return min(limit, 20)
        except ValueError:
            pass
    return 5


def extract_country(message: str) -> str:
    countries = re.findall(r"[A-Za-z\s]+", message)
    if countries:
        return countries[0]


def extract_budget(message: str) -> str:
    message_lower = message.lower()
    if "budget" in message_lower:
        return "budget"
    else:
        return "budget"


def extract_influencer_limit(message: str) -> int:
    message_lower = message.lower()
    if "influencer" in message_lower:
        return "influencer"
    else:
        return 5
