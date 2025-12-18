from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import (
    extract_followers,
    extract_platforms,
    extract_limit,
    extract_countries,
    extract_categories,
)
import traceback


async def node_requirements(state):
    try:
        print("Entering node_requirements")
        msg = state.get("user_message", "")

        new_platforms = extract_platforms(msg)
        limit = extract_limit(msg)
        new_countries = extract_countries(msg)
        new_categories = extract_categories(msg)
        new_followers = extract_followers(msg)

        info_updated = False
        if new_platforms:
            state["platform"] = new_platforms
            info_updated = True

        if limit is not None:
            if limit > 50:
                state["reply"] = (
                    "You can select **maximum 50 influencers only**.\n\n"
                    "Please enter a number between **1 and 50**.\n"
                    "🔢 Examples: 5, 10, 20, 50"
                )
                state["limit"] = None
                state["reply_sent"] = False
                return state

            if limit <= 0:
                state["reply"] = (
                    "⚠️ Number of influencers must be **greater than 0**.\n\n"
                    "Please enter a valid number (1–50)."
                )
                state["limit"] = None
                state["reply_sent"] = False
                return state

            state["limit"] = limit
            info_updated = True

        if new_countries:
            state["country"] = new_countries
            info_updated = True
        if new_categories:
            state["category"] = new_categories
            info_updated = True

        if new_followers:
            state["followers"] = new_followers
            info_updated = True

        if info_updated:
            state["reply_sent"] = False

        missing = missing_fields(state)

        if "platform" in missing:
            state["reply"] = (
                "👋 Welcome to iShout!\n\n"
                "Let's find the perfect influencers for your campaign 🎲\n\n"
                "Which social media platform are you targeting?\n\n"
                "📱 Available Platforms: Instagram, TikTok, YouTube"
            )
            return state

        if "category" in missing:
            state["reply"] = (
                f"Great! *{', '.join(state['platform'])}* it is!\n\n"
                "Now, what category or niche are you looking for?\n\n"
                "💡 Categories: Fashion, Beauty, Tech, Fitness, Food, Travel, Gaming"
            )
            return state

        if "country" in missing:
            state["reply"] = (
                f"Perfect! *{', '.join(state['category'])}* influencers coming up!\n\n"
                "Which country or region should these influencers be based in?\n\n"
                "🌍 Countries: UAE, Kuwait, Saudi Arabia, Qatar, Oman, Lebanon, Jordan, Iraq, Egypt"
            )
            return state

        if "limit" in missing:
            state["reply"] = (
                f"Got it! Looking for influencers in *{', '.join(state['country'])}*\n\n"
                "How many influencers would you like to connect with?\n\n"
                "🔢 Examples: 5, 10, 20, 50"
            )
            return state

        if "followers" in missing:
            state["reply"] = (
                f"Noted! We'll find *{state.get('limit')}* influencers for you.\n\n"
                "What follower range are you targeting?\n\n"
                "👥 Examples:\n"
                "• 50k (Micro influencers)\n"
                "• 200k (Mid-tier)\n"
                "• 500k+ (Macro influencers)\n"
                "• 1M+ (Mega influencers)"
            )
            return state
        state["reply"] = None
        state["ready_for_campaign"] = True
        print("Exiting node_requirements successfully")

        return state

    except Exception:
        traceback.print_exc()

        state["reply"] = (
            "⚠️ Sorry, something went wrong while processing your message.\n"
            "Please try again."
        )
        state["reply_sent"] = False
        return state


def missing_fields(state: ConversationState):
    missing = []
    for field in ["platform", "category", "country", "limit", "followers"]:
        value = state.get(field)
        if field == "limit":
            is_missing = value is None or (isinstance(value, int) and value <= 0)
        else:
            if isinstance(value, list):
                is_missing = len(value) == 0
            else:
                is_missing = value is None or value == []
        if is_missing:
            missing.append(field)
    return missing
