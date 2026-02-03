from app.model.whatsappconversation import ConversationState
from app.utils.extract_feilds import (
    extract_followers,
    extract_platforms,
    extract_limit,
    extract_countries,
    extract_categories,
)
import traceback


async def node_requirements(state):
    print("Entering into node_requirements")
    print("--------------------------------")
    try:
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
                "✨ Welcome to iShout! ✨\n\n"
                "Which platform do you want to promote on?🎲\n\n"
                "📸 Instagram – Visual storytelling & high engagement\n"
                "🎵 TikTok – Viral reach & trend-driven growth\n"
                "🎥 YouTube – Long-form impact & trust building\n\n"
                "👉 Just reply with the platform name to continue"
            )
            return state

        if "category" in missing:
            state["reply"] = (
                f"Perfect choice! ✨ *{', '.join(state['platform'])}* is a great pick.\n"
                "Now let’s narrow it down so we can match you with the *right influencers* 🎯\n\n"
                "Which category best fits your brand?\n"
                "💡 Available Categories:\n"
                "👗 Fashion\n"
                "💄 Beauty\n"
                "📱 Tech\n"
                "💪 Fitness\n"
                "🍔 Food\n"
                "✈️ Travel\n"
                "🎮 Gaming\n\n"
                "👉 Just reply with the category name."
            )
            return state

        if "country" in missing:
            state["reply"] = (
                f"Awesome choice! ✨ *{', '.join(state['category'])}* influencers are a great fit.\n"
                "Let’s make it even more precise so your campaign performs better 🎯\n\n"
                "Which country or region should your influencers be based in?\n\n"
                "🌍 Available Locations:\n"
                "🇦🇪 UAE\n"
                "🇰🇼 Kuwait\n"
                "🇸🇦 Saudi Arabia\n"
                "🇶🇦 Qatar\n"
                "🇴🇲 Oman\n"
                "🇱🇧 Lebanon\n"
                "🇯🇴 Jordan\n"
                "🇮🇶 Iraq\n"
                "🇪🇬 Egypt\n\n"
                "👉 Just reply with the country name."
            )
            return state

        if "limit" in missing:
            state["reply"] = (
                f"Perfect! 🌍 We’ll focus on influencers based in *{', '.join(state['country'])}*.\n"
                "Now let’s decide the reach of your campaign 🚀\n\n"
                "How many influencers would you like to collaborate with?\n\n"
                "🔢 Popular choices:\n"
                "✨ 5  – highly targeted\n"
                "🔥 10 – balanced reach\n"
                "🚀 20 – strong visibility\n"
                "🌍 50 – maximum exposure\n\n"
                "👉 Just reply with a number."
            )
            return state

        if "followers" in missing:
            state["reply"] = (
                f"Great! 🙌 We’ll line up *{state.get('limit')}* influencers for your campaign.\n"
                "Now let’s choose the *reach level* that fits your goals 🎯\n\n"
                "What follower range are you aiming for?\n\n"
                "👥 Popular options:\n"
                "✨ 50k+  – Micro (high engagement)\n"
                "🔥 200k+ – Mid-tier (balanced reach)\n"
                "🚀 500k+ – Macro (strong visibility)\n"
                "🌟 1M+   – Mega (maximum impact)\n\n"
                "👉 Just reply with the number (e.g., 50k, 200k)."
            )
            return state
        state["reply"] = None
        state["ready_for_campaign"] = True
        print("Exiting from node_requirements")
        print("--------------------------------")
        return state

    except Exception:
        traceback.print_exc()
        print("Exiting from node_requirements")
        print("--------------------------------")
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
