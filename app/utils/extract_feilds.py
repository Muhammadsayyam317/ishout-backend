import json
import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_campaign
from app.utils.extract_feilds import (
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

    if platform:
        state["platform"] = platform
    if limit is not None:
        state["number_of_influencers"] = limit
        logging.info(f"[node_requirements] Updated number_of_influencers to: {limit}")
    if country:
        state["country"] = country
    if category:
        state["category"] = category

    logging.info(
        f"[node_requirements] Extracted - platform: {platform}, category: {category}, country: {country}, limit: {limit}"
    )
    logging.info(
        f"[node_requirements] State after updates - platform: {state.get('platform')}, category: {state.get('category')}, country: {state.get('country')}, number_of_influencers: {state.get('number_of_influencers')}"
    )

    missing = missing_fields(state)
    logging.info(f"[node_requirements] Missing fields: {missing}")
    state["reply"] = None

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
        if state.get("number_of_influencers"):
            provided_items.append(
                f"{counter}) number of influencers: {state['number_of_influencers']}"
            )
            counter += 1

        needed = []
        if "platform" in missing:
            needed.append("platform (Instagram, TikTok, or YouTube)")
        if "country" in missing:
            needed.append("country (e.g., UAE, Kuwait, Saudi Arabia)")
        if "category" in missing:
            needed.append("category (e.g., fashion, beauty, food)")
        if "number_of_influencers" in missing:
            needed.append("number of influencers")

        if provided_items:
            reply = "Thanks! I got:\n"
            reply += "\n".join(provided_items)
            reply += "\n\n"
            reply += f"I still need: {', '.join(needed)}.\n\n"
            reply += "Please provide the missing details."
        else:
            reply = "To help you find the right influencers, I need:\n"
            reply += "• " + "\n• ".join(needed) + "\n\n"
            reply += "Please provide all these details in your message."

        state["reply"] = reply
    else:
        state["reply"] = None
        logging.info(
            "[node_requirements] All fields present, reply set to None - should proceed to create_campaign"
        )

    return state


async def node_ask_user(state, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
    return state


async def node_create_campaign(state: ConversationState):
    result = await create_campaign(state)
    state["campaign_id"] = result["campaign_id"]
    state["campaign_created"] = True
    state["reply"] = None
    return state


async def node_acknowledge_user(state, config):
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
        is_missing = (
            value is None
            or value == ""
            or (field == "number_of_influencers" and value == 0)
        )
        if is_missing:
            missing.append(field)
        logging.info(
            f"[missing_fields] {field}: {repr(value)} (type: {type(value).__name__}, missing: {is_missing})"
        )
    logging.info(f"[missing_fields] Final missing list: {missing}")
    return missing
