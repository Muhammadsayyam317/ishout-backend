from langgraph.graph import StateGraph, END
from app.agents.nodes.requirments import (
    node_acknowledge_user,
    node_ask_user,
    node_create_campaign,
    node_debug_after,
    node_debug_before,
    node_requirements,
)
from app.models.whatsappconversation_model import ConversationState

graph = StateGraph(ConversationState)

# Add all nodes
graph.add_node("debug_before", node_debug_before)
graph.add_node("requirements", node_requirements)
graph.add_node("debug_after", node_debug_after)
graph.add_node("ask_user", node_ask_user)
graph.add_node("create_campaign", node_create_campaign)
graph.add_node("acknowledge_user", node_acknowledge_user)

# Entry point
graph.set_entry_point("debug_before")
graph.add_edge("debug_before", "requirements")
graph.add_edge("requirements", "debug_after")

graph.add_conditional_edges(
    "debug_after",
    lambda state: (
        "create_campaign"
        if state.get("ready_for_campaign")
        else (
            "ask_user"
            if state.get("reply") and not state.get("reply_sent")
            else "requirements"
        )
    ),
    {
        "ask_user": "ask_user",
        "create_campaign": "create_campaign",
        "requirements": "requirements",
    },
)

graph.add_edge("ask_user", "debug_after")
graph.add_edge("create_campaign", "acknowledge_user")
graph.add_edge("acknowledge_user", END)
