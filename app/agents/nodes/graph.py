from langgraph.graph import StateGraph, END
from app.agents.nodes.message_type import identify_message_type
from app.agents.nodes.message_classification import message_classification
from app.agents.nodes.query_llm import Query_to_llm
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.models.whatsappconversation_model import ConversationState
from app.utils.extract_feilds import extract_all_fields
from langgraph.checkpoint.memory import InMemorySaver


checkpointer = InMemorySaver()
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


# Node 3: Check missing fields
async def node_requirements(state: ConversationState):

    fields = extract_all_fields(state["user_message"])
    missing = []

    for key, val in fields.items():
        state[key] = val
        if val is None:
            missing.append(key)

    if missing:
        state["reply"] = f"I need these details before searching: {', '.join(missing)}"
        return "ask_user"

    return "search"


# Ask user missing fields
async def node_ask_user(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return END


# Node 4: Search influencers
async def node_search(state: ConversationState):
    result = await Query_to_llm(state["user_message"])
    state["reply"] = result
    return "send"


# Node 5: Send reply
async def node_send(state: ConversationState):
    await send_whatsapp_message(state["sender_id"], state["reply"])
    return END


# Build graph

graph.add_node("identify", node_identify)
graph.add_node("classify", node_classify)
graph.add_node("requirements", node_requirements)
graph.add_node("ask_user", node_ask_user)
graph.add_node("search", node_search)
graph.add_node("send", node_send)

graph.set_entry_point("identify")

graph.add_edge("identify", "classify")
graph.add_edge("classify", "requirements")

graph.add_conditional_edges(
    "requirements",
    lambda state: "ask_user" if state.get("reply") else "search",
    {
        "ask_user": "ask_user",
        "search": "search",
    },
)

graph.add_edge("search", "send")
graph.add_edge("send", END)

whatsapp_agent = graph.compile(checkpointer=checkpointer)
