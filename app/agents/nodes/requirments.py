import json
import logging
from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import (
    extract_followers,
    extract_platforms,
    extract_limit,
    extract_countries,
    extract_categories,
)
from app.utils.helpers import format_list_with_count


async def node_debug_before(state):
    logging.info("\n\n===== DEBUG BEFORE =====\n" + json.dumps(state, indent=2))
    return state


async def node_debug_after(state):
    logging.info("\n\n===== DEBUG AFTER =====\n" + json.dumps(state, indent=2))
    return state


async def node_requirements(state):
    print("➡ Entered node_requirements")
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
        platforms = ["Instagram", "TikTok", "YouTube"]
        state["reply"] = (
            "👋 Welcome to iShout!\n\n"
            "Let's find the perfect influencers for your campaign 🎲\n\n"
            "Which social media platform are you targeting?\n\n"
            "📱 Available Social Platforms:\n\n"
            f"{format_list_with_count(platforms, '📱')}\n\n"
        )
        return state
    if "category" in missing:
        categories = ["Fashion", "Beauty", "Sports", "Fitness", "Food"]
        state["reply"] = (
            f"Great! *{', '.join(state['platform'])}* it is!\n\n"
            "Now, what category or niche are you looking for?\n\n"
            "💡 Catefories:\n"
            f"{format_list_with_count(categories)}\n\n"
            "and more categories are available",
        )
        return state
    if "country" in missing:
        countries = ["UAE", "Kuwait", "Saudi Arabia", "Qatar", "Oman"]
        state["reply"] = (
            f"Perfect! *{', '.join(state['category'])}* influencers coming up!\n\n"
            "Which country or region should these influencers be based in?\n\n"
            "🌍Countries:\n",
            f"{format_list_with_count(countries)}\n\n"
            "and more countires are available",
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
        followers = [
            "50k (Micro influencers)",
            "200k (Mid-tier)",
            "500k+ (Macro influencers)",
            "1M+ (Mega influencers)",
        ]
        state["reply"] = (
            f"Noted! We'll find *{state.get('limit')}* influencers for you.\n\n"
            "What follower range are you targeting?\n\n"
            "👥 Follower Ranges:\n"
            f"{format_list_with_count(followers)}\n\n"
            "and more follower ranges are available",
        )
        return state

    state["reply"] = None
    state["ready_for_campaign"] = True
    print(f"➡ Exited node_requirements: {state}")
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
