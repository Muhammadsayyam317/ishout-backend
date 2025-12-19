from langgraph.graph import StateGraph, END
from app.agents.nodes.requirments import (
    node_requirements,
)
from app.agents.nodes.create_campaign_node import node_create_campaign
from app.agents.nodes.acknowledge_user_node import node_acknowledge_user
from app.agents.nodes.verify_user import node_verify_user
from app.agents.nodes.send_reply import node_send_reply
from app.models.whatsappconversation_model import ConversationState

graph = StateGraph(ConversationState)

graph.add_node("verify_user", node_verify_user)
graph.add_node("requirements", node_requirements)
graph.add_node("create_campaign", node_create_campaign)
graph.add_node("acknowledge_user", node_acknowledge_user)
graph.add_node("send_reply", node_send_reply)

graph.set_entry_point("verify_user")
graph.add_conditional_edges(
    "verify_user",
    lambda state: "requirements" if state.get("is_existing_user") else "send_reply",
    {
        "requirements": "requirements",
        "send_reply": "send_reply",
    },
)

graph.add_edge("requirements", "create_campaign")
graph.add_conditional_edges(
    "create_campaign",
    lambda state: (
        "acknowledge_user" if state.get("ready_for_campaign") else "send_reply"
    ),
    {
        "acknowledge_user": "acknowledge_user",
        "send_reply": "send_reply",
    },
)
graph.add_edge("acknowledge_user", "send_reply")
graph.add_edge("send_reply", END)
