from langgraph.graph import StateGraph, END
from app.agents.nodes.query_llm import Query_to_llm
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import (
    extract_platform,
    extract_limit,
    extract_country,
    extract_category,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
import logging

checkpointer = MemorySaver()
store = InMemoryStore()
graph = StateGraph(ConversationState)


# Node 1: Extract requirements into state (platform, count, country,number of influencers)
async def node_requirements(state):
    logging.info(f"[requirements] User message: {state['user_message']}")
    state.pop("reply", None)
    msg = state.get("user_message") or ""

    # Extract fields from the latest user message
    platform = extract_platform(msg)
    limit = extract_limit(msg)
    country = extract_country(msg)
    category = extract_category(msg)

    # Accumulate in state (do not overwrite existing if None)
    if platform:
        state["platform"] = platform
    if limit is not None:
        state["number_of_influencers"] = limit
    if country:
        state["country"] = country
    if category:
        state["category"] = category

    # Check missing fields
    missing = missing_fields(state)
    if missing:
        pretty = []
        for m in missing:
            if m == "platform":
                pretty.append("platform (Instagram, TikTok, YouTube)")
            elif m == "country":
                pretty.append("country (UAE, Kuwait, etc.)")
            elif m == "number_of_influencers":
                pretty.append("number of influencers")
            elif m == "category":
                pretty.append("category (fashion, beauty, etc.)")
        state["reply"] = (
            "I need these details before searching: "
            + ", ".join(pretty)
            + ".\nPlease reply with them, for example: "
            "'Platform is Instagram, category is fashion, country is UAE, and I need 4 influencers.'"
        )

    return state


# Ask user missing fields
async def node_ask_user(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return state


# Node 2: Search influencers
async def node_search(state: ConversationState):
    result = await Query_to_llm(state)
    state["reply"] = result
    return state


# Node 3: Send reply
async def node_send(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return state


def missing_fields(state: ConversationState):
    missing = []
    if not state.get("platform"):
        missing.append("platform")
    if not state.get("country"):
        missing.append("country")
    if not state.get("number_of_influencers"):
        missing.append("number_of_influencers")
    if not state.get("category"):
        missing.append("category")
    return missing


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

whatsapp_agent = graph.compile(checkpointer=checkpointer, store=store)
