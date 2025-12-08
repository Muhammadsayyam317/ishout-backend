import json
import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.state import reset_user_state, update_user_state
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_whatsapp_campaign
from app.utils.extract_feilds import (
    extract_followers,
    extract_platforms,
    extract_limit,
    extract_countries,
    extract_categories,
)


async def node_debug_before(state):
    logging.info("\n\n===== DEBUG BEFORE =====\n" + json.dumps(state, indent=2))
    return state


async def node_debug_after(state):
    logging.info("\n\n===== DEBUG AFTER =====\n" + json.dumps(state, indent=2))
    return state


async def node_requirements(state):
    print("➡ Entered node_requirements")
    msg = state.get("user_message", "")

    # Extract details
    new_platforms = extract_platforms(msg)
    limit = extract_limit(msg)
    new_countries = extract_countries(msg)
    new_categories = extract_categories(msg)
    new_followers = extract_followers(msg)

    if new_platforms:
        state["platform"] = new_platforms

    if limit is not None:
        state["limit"] = limit

    if new_countries:
        state["country"] = new_countries

    if new_categories:
        state["category"] = new_categories

    if new_followers:
        state["followers"] = new_followers

    missing = missing_fields(state)

    if "platform" in missing:
        state["reply"] = (
            "Great! Let's get started\n\n"
            "Which platform should the influencers be from?\n"
            "Instagram, TikTok, or YouTube?"
        )
        return state

    if "category" in missing:
        state["reply"] = (
            f"Thanks! Platform selected: {', '.join(state['platform'])}\n\n"
            "Now tell me the *category* you're targeting.\n"
            "For example: fashion, beauty, tech, food, travel."
        )
        return state

    if "country" in missing:
        state["reply"] = (
            f"Category saved: {', '.join(state['category'])}\n\n"
            "Which *country* should the influencers be from?\n"
            "e.g., UAE, Saudi Arabia, Kuwait, Qatar"
        )
        return state

    if "limit" in missing:
        state["reply"] = (
            f"Country saved: {', '.join(state['country'])}\n\n"
            "How many influencers do you want?\n"
            "Example: 5, 10, 20"
        )
        return state

    if "followers" in missing:
        state["reply"] = (
            f"Perfect! Number of influencers saved: {state['limit']}\n\n"
            "What follower range do you want?\n"
            "Examples: 10k, 50k-100k, 1M+"
        )
        return state

    state["reply"] = (
        "Awesome! 🎉 I now have all the details:\n\n"
        f"• Platform: {', '.join(state['platform'])}\n"
        f"• Category: {', '.join(state['category'])}\n"
        f"• Country: {', '.join(state['country'])}\n"
        f"• Number of influencers: {state['limit']}\n"
        f"• Followers range: {', '.join(state['followers'])}\n\n"
        "iShout is fetching the best influencers for you.Once Admin approves your request, we will share the matching influencers with you."
    )
    state["ready_for_campaign"] = True
    state["reply_sent"] = False
    print(f"➡ State after node_requirements: {state}")
    return state


async def node_ask_user(state, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply") and not state.get("reply_sent"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
        await update_user_state(sender, state)
    return state


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")
    result = await create_whatsapp_campaign(state)
    state["campaign_id"] = result["campaign_id"]
    state["campaign_created"] = True
    state["reply"] = None
    print(f"➡ State after node_create_campaign: {state}")
    return state


async def node_acknowledge_user(state: ConversationState, config):
    print("➡ Entered node_acknowledge_user")
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    final_msg = (
        "Great! I got all your campaign details.\n\n"
        "1) Platform is: " + ", ".join(state["platform"]) + "\n"
        "2) Category is: " + ", ".join(state["category"]) + "\n"
        "3) Country is: " + ", ".join(state["country"]) + "\n"
        "4) Followers count: " + ", ".join(state["followers"]) + "\n"
        "5) Number of influencers: " + str(state["limit"]) + "\n"
        "iShout admin team will review them and we’ll notify you once it's approved.\n"
        "Thank you for using iShout! 🎉"
    )
    await send_whatsapp_message(sender, final_msg)
    cleared_state = await reset_user_state(sender)
    print(f"➡ Cleared state: {cleared_state}")
    return cleared_state


def missing_fields(state: ConversationState):
    missing = []
    for field in [
        "platform",
        "country",
        "limit",
        "category",
        "followers",
    ]:
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
