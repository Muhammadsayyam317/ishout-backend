import json
import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.state import update_user_state
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_campaign
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
    msg = state.get("user_message", "")
    if state.get("done"):
        state["reply"] = "Conversation already completed, skipping"
        return state

    # Extract new values from current message
    new_platforms = extract_platforms(msg)
    limit = extract_limit(msg)
    new_countries = extract_countries(msg)
    new_categories = extract_categories(msg)
    new_followers = extract_followers(msg)

    # Set new values - the merge_arrays reducer will handle merging with existing values
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

    if missing:
        provided_items = []
        counter = 1

        platforms = state.get("platform") or []
        if platforms:
            platform_list = (
                [p.title() for p in platforms]
                if isinstance(platforms, list)
                else [platforms.title()]
            )
            provided_items.append(f"{counter}) Platform: {', '.join(platform_list)}")
            counter += 1

        categories = state.get("category") or []
        if categories:
            category_list = (
                [c.title() for c in categories]
                if isinstance(categories, list)
                else [categories.title()]
            )
            provided_items.append(f"{counter}) Category: {', '.join(category_list)}")
            counter += 1

        countries = state.get("country") or []
        if countries:
            country_list = []
            for c in countries if isinstance(countries, list) else [countries]:
                country_display = c.upper() if len(c) <= 4 else c.title()
                country_list.append(country_display)
            provided_items.append(f"{counter}) Country: {', '.join(country_list)}")
            counter += 1

        if state.get("limit"):
            provided_items.append(f"{counter}) Number of influencers: {state['limit']}")
            counter += 1

        followers = state.get("followers") or []
        if followers:
            follower_list = followers if isinstance(followers, list) else [followers]
            provided_items.append(
                f"{counter}) Followers count: {', '.join(follower_list)}"
            )
            counter += 1

        needed = []
        if "platform" in missing:
            needed.append("Platform (Instagram, TikTok, or YouTube)")
        if "country" in missing:
            needed.append("Country (e.g., UAE, Kuwait, Saudi Arabia)")
        if "category" in missing:
            needed.append("Category (e.g., fashion, beauty, food)")
        if "limit" in missing:
            needed.append("Number of influencers (e.g., 10, 20, 30)")
        if "followers" in missing:
            needed.append("Followers count (e.g., 10k, 2M, 3000K)")

        if provided_items:
            reply = "Thanks! I got:\n" + "\n".join(provided_items) + "\n\n"
            reply += f"I still need: {', '.join(needed)}.\n\nPlease provide the missing details."
        else:
            reply = "To help you find the right influencers, I need:\n• " + "\n• ".join(
                needed
            )
            reply += "\n\nPlease provide all these details in your message."

        state["reply"] = reply
        state["done"] = False
        return state

    state["reply"] = None
    state["reply_sent"] = False
    state["done"] = True

    return state


async def node_ask_user(state, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply") and not state.get("reply_sent"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
        await update_user_state(sender, state)
    return state


async def node_create_campaign(state: ConversationState):
    payload = {
        "platform": state.get("platform"),
        "category": state.get("category"),
        "country": state.get("country"),
        "limit": state.get("limit"),
        "followers": state.get("followers"),
        "user_id": state.get("sender_id"),
        "source": "whatsapp",
    }
    result = await create_campaign(payload)
    state["campaign_id"] = result["campaign_id"]
    state["campaign_created"] = True
    state["reply"] = None
    return state


async def node_acknowledge_user(state: ConversationState, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    final_msg = (
        "Great! I got all your campaign details.\n"
        "iShout admin team will review them and we’ll notify you once it's approved.\n"
        "Thank you for using iShout! 🎉"
    )
    await send_whatsapp_message(sender, final_msg)
    state["done"] = True
    state["reply_sent"] = True
    return state


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
            # For list fields, check if empty list or None
            if isinstance(value, list):
                is_missing = len(value) == 0
            else:
                is_missing = value is None or value == []
        if is_missing:
            missing.append(field)
    return missing
