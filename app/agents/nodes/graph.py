from langgraph.graph import StateGraph, END
from app.agents.nodes.message_type import identify_message_type
from app.agents.nodes.message_classification import message_classification
from app.agents.nodes.query_llm import Query_to_llm
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import (
    extract_platform,
    extract_limit,
    extract_country,
    extract_budget,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore


# In-memory checkpointer + store for testing (no disk persistence)
checkpointer = MemorySaver()
store = InMemoryStore()
graph = StateGraph(ConversationState)


# Node 1: Identify incoming message
async def node_identify(state: ConversationState):
    msg_data = await identify_message_type(state["event_data"])
    state["sender_id"] = msg_data["sender_id"]
    state["user_message"] = msg_data["message_text"]
    return state


# Node 2: Classify intent
async def node_classify(state: ConversationState):
    result = await message_classification(state["user_message"])
    state["intent"] = result.intent
    return state


# Node 3: Extract/accumulate requirements into state (platform, count, country, budget)
async def node_requirements(state):
    # Clear old reply every time user sends new message
    state.pop("reply", None)

    msg = state.get("user_message") or ""

    # extract only from current message
    platform = extract_platform(msg)
    limit = extract_limit(msg)
    country = extract_country(msg)
    budget = extract_budget(msg)
    category = None
    try:
        from app.utils.extract_feilds import extract_category

        category = extract_category(msg)
    except Exception:
        category = None

    # accumulate (do not overwrite with None)
    if platform:
        state["platform"] = platform
    if limit is not None:
        state["number_of_influencers"] = limit
    if country:
        state["country"] = country
    if budget:
        state["budget"] = budget
    if category:
        state["category"] = category

    # compute missing fields using the shared helper
    missing = missing_fields(state)
    # include category in missing checklist if you want it mandatory
    # if not state.get("category"):
    #     missing.append("category")

    if missing:
        # keep the user-facing friendly names and examples
        pretty = []
        for m in missing:
            if m == "platform":
                pretty.append("platform (e.g. Instagram, TikTok, YouTube)")
            elif m == "country":
                pretty.append("country (e.g. UAE, Kuwait, Saudi Arabia)")
            elif m == "limit":
                pretty.append("number of influencers")
            else:
                pretty.append(m)
        state["reply"] = (
            "I need these details before searching: "
            + ", ".join(pretty)
            + ".\nPlease reply with them, for example: "
            "'Platform is Instagram, category is fashion, country is UAE, and I need 4 influencers.'"
        )

    return state


# Greet user and explain capabilities
async def node_greet(state: ConversationState):
    state["reply"] = "Hi! 👋 I can help you find influencers..."
    return state


async def node_fallback(state: ConversationState):
    state["reply"] = "I can only help you find influencers..."
    return state


# Ask user missing fields
async def node_ask_user(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return state


# Node 4: Search influencers
async def node_search(state: ConversationState):
    # Delegate to LLM/query layer, which will read fields from state
    result = await Query_to_llm(state)
    state["reply"] = result
    return state


# Node 5: Send reply
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
        missing.append("limit")

    return missing


# Build graph

graph.add_node("identify", node_identify)
graph.add_node("classify", node_classify)
graph.add_node("requirements", node_requirements)
graph.add_node("ask_user", node_ask_user)
graph.add_node("search", node_search)
graph.add_node("send", node_send)
graph.add_node("greet", node_greet)
graph.add_node("fallback", node_fallback)

graph.set_entry_point("identify")

graph.add_edge("identify", "classify")
graph.add_edge("classify", "requirements")
graph.add_conditional_edges(
    "requirements",
    lambda state: "ask_user" if missing_fields(state) else "search",
    {"ask_user": "ask_user", "search": "search"},
)


graph.add_edge("ask_user", END)
graph.add_edge("search", "send")
graph.add_edge("send", END)

whatsapp_agent = graph.compile(checkpointer=checkpointer, store=store)
