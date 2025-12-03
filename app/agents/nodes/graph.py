from langgraph.graph import StateGraph, END
from app.agents.nodes.query_llm import Query_to_llm
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.state import reset_user_state
from app.models.whatsappconversation_model import ConversationState
import logging
from app.utils.extract_feilds import (
    extract_platform,
    extract_limit,
    extract_country,
    extract_category,
)

graph = StateGraph(ConversationState)


async def node_requirements(state: ConversationState):
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


# Node 2: Search influencers
async def node_search(state: ConversationState):
    logging.info("[node_search] Entering node_search")
    logging.info(f"[node_search] Full state before LLM call: {state}")
    logging.info(
        f"[node_search] State values - platform: {state.get('platform')}, country: {state.get('country')}, number_of_influencers: {state.get('number_of_influencers')}, category: {state.get('category')}, sender_id: {state.get('sender_id')}, user_message: {state.get('user_message')}"
    )
    result = await Query_to_llm(state)
    logging.info(f"[node_search] Result from LLM: {result}")
    logging.info("[node_search] Exiting node_search")
    state["reply"] = result
    return state


# Node 3: Send reply
async def node_send(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    reset_user_state(state["sender_id"])
    return state


def missing_fields(state: ConversationState):
    logging.info(f"[missing_fields] State: {state}")
    return [
        field
        for field in ["platform", "country", "number_of_influencers", "category"]
        if not state.get(field)
    ]


# Build graph

graph.add_node("requirements", node_requirements)
graph.add_node("ask_user", node_ask_user)
graph.add_node("search", node_search)
graph.add_node("send", node_send)

graph.set_entry_point("requirements")

graph.add_conditional_edges(
    "requirements",
    lambda state: "ask_user" if state.get("reply") else "search",
    {
        "ask_user": "ask_user",
        "search": "search",
    },
)


graph.add_edge("ask_user", END)
graph.add_edge("search", "send")
graph.add_edge("send", END)
# graph.add_edge("requirements", END)
