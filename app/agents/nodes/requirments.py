import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.query_llm import Query_to_llm
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_campaign
from app.utils.extract_feilds import (
    extract_platform,
    extract_limit,
    extract_country,
    extract_category,
)


async def node_debug_before(state: dict):
    logging.info("\n\n===== DEBUG BEFORE =====\n" + json.dumps(state, indent=2))
    return state


async def node_debug_after(state: dict):
    logging.info("\n\n===== DEBUG AFTER =====\n" + json.dumps(state, indent=2))
    return state


async def node_requirements(state: ConversationState):
    msg = state.get("user_message", "")
    logging.info(f"[node_requirements] User message: {msg}")
    if state.get("done"):
        state["reply"] = "Conversation already completed, skipping"
        return state

    msg = state.get("user_message", "")
    logging.info(f"[node_requirements] User message: {msg}")

    # Extract new fields from message
    platform = extract_platform(msg)
    limit = extract_limit(msg)
    country = extract_country(msg)
    category = extract_category(msg)

    # (do NOT overwrite correct previous values)
    if platform:
        state["platform"] = platform
    if limit is not None:
        state["number_of_influencers"] = limit
    if country:
        state["country"] = country
    if category:
        state["category"] = category

    # Check what is still missing
    missing = missing_fields(state)

    if missing:
        pretty = []

        if "platform" in missing:
            pretty.append("platform (Instagram, TikTok, YouTube)")
        if "country" in missing:
            pretty.append("country (UAE, Kuwait, etc.)")
        if "category" in missing:
            pretty.append("category (fashion, beauty, etc.)")
        if "number_of_influencers" in missing:
            pretty.append("number of influencers")

        state["reply"] = (
            "iShout need these details before searching: "
            + ", ".join(pretty)
            + ".\nPlease reply with them."
        )
    else:
        state["reply"] = None

    return state


# Ask user missing fields
async def node_ask_user(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return state


# async def node_create_campaign(state: ConversationState):
#     result = await create_campaign(state)
#     state["campaign_id"] = result["campaign_id"]
#     state["reply"] = result["message"]
#     return state


# Node 2: Search influencers
async def node_search(state: ConversationState):
    result = await Query_to_llm(state)
    state["reply"] = result
    return state


# Node 3: Send reply
async def node_send(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    state["done"] = True
    return state


def missing_fields(state: ConversationState):
    logging.info(f"[missing_fields] State: {state}")
    return [
        field
        for field in ["platform", "country", "number_of_influencers", "category"]
        if not state.get(field)
    ]
