from langgraph.graph import StateGraph, END
from app.agents.nodes.requirments import (
    node_ask_user,
    node_requirements,
    node_search,
    node_send,
)
from app.models.whatsappconversation_model import ConversationState

graph = StateGraph(ConversationState)

# Build graph
graph.add_node("requirements", node_requirements)
graph.add_node("ask_user", node_ask_user)
# graph.add_node("create_campaign", node_create_campaign)
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
# graph.add_edge("create_campaign", "search")
graph.add_edge("search", "send")
graph.add_edge("send", END)
