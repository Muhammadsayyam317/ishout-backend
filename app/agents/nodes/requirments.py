import json
import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.state import update_user_state
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_campaign
from app.utils.extract_feilds import (
    extract_followers,
    extract_platform,
    extract_limit,
    extract_country,
    extract_category,
)


async def node_debug_before(state, config):
    logging.info("\n\n===== DEBUG BEFORE =====\n" + json.dumps(state, indent=2))
    return state


async def node_debug_after(state, config):
    logging.info("\n\n===== DEBUG AFTER =====\n" + json.dumps(state, indent=2))
    return state


async def node_requirements(state, config):
    msg = state.get("user_message", "")
    if state.get("done"):
        state["reply"] = "Conversation already completed, skipping"
        return state

    platform = extract_platform(msg)
    limit = extract_limit(msg)
    country = extract_country(msg)
    category = extract_category(msg)
    followers = extract_followers(msg)

    if platform:
        state["platform"] = platform
    if limit is not None:
        state["limit"] = limit
        logging.info(f"[node_requirements] Updated number_of_influencers to: {limit}")
    if country:
        state["country"] = country
    if category:
        state["category"] = category
    if followers:
        state["followers"] = followers

    logging.info(
        f"[node_requirements] State after updates - platform: {state.get('platform')}, category: {state.get('category')}, country: {state.get('country')}, number_of_influencers: {state.get('number_of_influencers')}"
    )

    missing = missing_fields(state)
    logging.info(f"[node_requirements] Missing fields: {missing}")

    if missing:
        provided_items = []
        counter = 1

        if state.get("platform"):
            provided_items.append(f"{counter}) platform: {state['platform'].title()}")
            counter += 1

        if state.get("category"):
            provided_items.append(f"{counter}) category: {state['category'].title()}")
            counter += 1

        if state.get("country"):
            country_display = (
                state["country"].upper()
                if len(state["country"]) <= 4
                else state["country"].title()
            )
            provided_items.append(f"{counter}) country: {country_display}")
            counter += 1

        if state.get("limit"):
            provided_items.append(f"{counter}) number of influencers: {state['limit']}")
            counter += 1
        if state.get("followers"):
            provided_items.append(f"{counter}) followers: {state['followers']}")
            counter += 1

        needed = []
        if "platform" in missing:
            needed.append("platform (Instagram, TikTok, or YouTube)")
        if "country" in missing:
            needed.append("country (e.g., UAE, Kuwait, Saudi Arabia)")
        if "category" in missing:
            needed.append("category (e.g., fashion, beauty, food)")
        if "limit" in missing:
            needed.append("number of influencers")
        if "followers" in missing:
            needed.append("followers")

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

    logging.info(
        "[node_requirements] All fields present. reply=None, done=True → proceed to create_campaign"
    )

    return state


async def node_ask_user(state, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply") and not state.get("reply_sent"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
        await update_user_state(sender, state)
    return state


async def node_create_campaign(state: ConversationState, config):
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
        "Great! 🎉 I got all your campaign details.\n"
        "iShout admin team will review them and we’ll notify you once it's approved. 👍"
    )
    await send_whatsapp_message(sender, final_msg)
    state["done"] = True
    state["reply_sent"] = True
    return state


def missing_fields(state: ConversationState):
    missing = []
    for field in ["platform", "country", "number_of_influencers", "category"]:
        value = state.get(field)
        if field == "number_of_influencers":
            is_missing = value is None or (isinstance(value, int) and value <= 0)
        else:
            is_missing = value is None or value == ""
        if is_missing:
            missing.append(field)
        logging.info(f"[missing_fields] {field}: {repr(value)} (missing: {is_missing})")
    logging.info(f"[missing_fields] Final missing list: {missing}")
    return missing
