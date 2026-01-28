from langgraph.graph import StateGraph, END
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.analyzes_intent import analyze_intent
from app.agents.Instagram.nodes.determine_next_action import determine_next_action
from app.agents.Instagram.nodes.finalize_negotiation import finalize_negotiation
from app.agents.Instagram.nodes.generate_ai_reply import generate_ai_reply
from app.agents.Instagram.nodes.handle_rejection_node import handle_rejection
from app.agents.Instagram.nodes.normalize_state import normalize_state
from app.agents.Instagram.nodes.mannual_negotiation_node import (
    manual_negotiation_required,
)
from app.agents.Instagram.nodes.step_node import route_next_step
from app.agents.Instagram.nodes.store_conversation_node import store_conversation
from app.agents.Instagram.nodes.fetch_influencer_price_node import fetch_pricing_rules
from app.agents.Instagram.nodes.pricing_negotiation_node import pricing_negotiation
from app.agents.Instagram.nodes.Send_reply_node import send_reply

graph = StateGraph(InstagramConversationState)

graph.set_entry_point("normalize_state")

# Nodes
graph.add_node("normalize_state", normalize_state)
graph.add_node("store_conversation", store_conversation)
graph.add_node("analyze_intent", analyze_intent)
graph.add_node("determine_next_action", determine_next_action)

graph.add_node("handle_rejection", handle_rejection)

graph.add_node("fetch_pricing_rules", fetch_pricing_rules)
graph.add_node("pricing_negotiation", pricing_negotiation)
graph.add_node("manual_negotiation_required", manual_negotiation_required)
graph.add_node("finalize_negotiation", finalize_negotiation)

graph.add_node("generate_ai_reply", generate_ai_reply)
graph.add_node("send_reply", send_reply)


graph.add_edge("normalize_state", "store_conversation")
graph.add_edge("store_conversation", "analyze_intent")
graph.add_edge("analyze_intent", "determine_next_action")
graph.add_conditional_edges(
    "determine_next_action",
    route_next_step,
    {
        "handle_rejection": "handle_rejection",
        "generate_ai_reply": "generate_ai_reply",
        "fetch_pricing_rules": "fetch_pricing_rules",
    },
)
graph.add_edge("handle_rejection", "generate_ai_reply")
graph.add_edge("fetch_pricing_rules", "pricing_negotiation")
graph.add_edge("pricing_negotiation", "manual_negotiation_required")
graph.add_edge("manual_negotiation_required", "finalize_negotiation")
graph.add_edge("finalize_negotiation", "generate_ai_reply")
graph.add_edge("generate_ai_reply", "send_reply")
graph.add_edge("send_reply", END)


instagram_graph = graph.compile()
