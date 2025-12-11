from langgraph.graph import StateGraph, END
from app.agents.nodes.requirments import (
    node_debug_after,
    node_debug_before,
    node_requirements,
)
from app.agents.nodes.ask_user_node import node_ask_user
from app.agents.nodes.create_campaign_node import node_create_campaign
from app.agents.nodes.acknowledge_user_node import node_acknowledge_user
from app.models.whatsappconversation_model import ConversationState
from app.agents.nodes.verify_user import node_verify_user

graph = StateGraph(ConversationState)

graph.add_node("debug_before", node_debug_before)
graph.add_node("verify_user", node_verify_user)
graph.add_node("requirements", node_requirements)
graph.add_node("debug_after", node_debug_after)
graph.add_node("ask_user", node_ask_user)
graph.add_node("create_campaign", node_create_campaign)
graph.add_node("acknowledge_user", node_acknowledge_user)


graph.set_entry_point("debug_before")
graph.add_edge("debug_before", "verify_user")
graph.add_conditional_edges(
    "verify_user",
    lambda state: "requirements" if state.get("is_existing_user") else END,
    {"requirements": "requirements", END: END},
)

graph.add_edge("requirements", "debug_after")
graph.add_conditional_edges(
    "debug_after",
    lambda state: (
        "create_campaign"
        if state.get("ready_for_campaign")
        else ("ask_user" if state.get("reply") and not state.get("reply_sent") else END)
    ),
    {"ask_user": "ask_user", "create_campaign": "create_campaign", END: END},
)


graph.add_edge("ask_user", END)
graph.add_edge("create_campaign", "acknowledge_user")
graph.add_edge("acknowledge_user", END)
