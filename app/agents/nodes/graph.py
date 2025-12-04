from langgraph.graph import StateGraph, END
from app.agents.nodes.requirments import (
    node_ask_user,
    node_debug_after,
    node_debug_before,
    node_requirements,
    node_search,
    node_send,
)
from app.models.whatsappconversation_model import ConversationState

graph = StateGraph(ConversationState)

# Build graph

graph.add_node("debug_before", node_debug_before)
graph.add_node("debug_after", node_debug_after)

graph.add_node("requirements", node_requirements)
graph.add_node("ask_user", node_ask_user)
# graph.add_node("create_campaign", node_create_campaign)
graph.add_node("search", node_search)
graph.add_node("send", node_send)

graph.set_entry_point("requirements")

# Entry
graph.set_entry_point("debug_before")
# BEFORE -> requirements
graph.add_edge("debug_before", "requirements")
# After every node, go to debug_after
graph.add_edge("requirements", "debug_after")
graph.add_edge("ask_user", "debug_after")
graph.add_edge("search", "debug_after")
graph.add_edge("send", "debug_after")


graph.add_conditional_edges(
    "debug_after",
    lambda state: (
        "ask_user"
        if state.get("reply") and not state.get("done")
        else "search" if not state.get("done") else "send"
    ),
    {
        "ask_user": "ask_user",
        "search": "search",
        "send": "send",
    },
)
# graph.add_edge("create_campaign", "search  ")
graph.add_edge("send", END)
graph.add_edge("ask_user", END)
