from langgraph.graph import StateGraph, END
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.normalize_state import normalize_state
from app.agents.Instagram.nodes.store_conversation_node import store_conversation
from app.agents.Instagram.nodes.analyzes_intent import analyze_intent
from app.agents.Instagram.nodes.ask_missing_info import (
    ask_missing_info,
    ask_missing_info_next,
    pricing_negotiation_next,
)
from app.agents.Instagram.nodes.fetch_influencer_price_node import fetch_pricing_rules
from app.agents.Instagram.nodes.pricing_negotiation_node import pricing_negotiation
from app.agents.Instagram.nodes.mannual_negotiation_node import (
    manual_negotiation_required,
)
from app.agents.Instagram.nodes.finalize_negotiation import finalize_negotiation
from app.agents.Instagram.nodes.generate_ai_reply import generate_ai_reply
from app.agents.Instagram.nodes.Send_reply_node import send_reply
from app.agents.Instagram.nodes.handle_rejection_node import handle_rejection
from app.agents.Instagram.session.instauser_session import instauser_session
from app.utils.custom_logging import insta_debug_before, insta_debug_after


# --- Create Graph ---
graph = StateGraph(InstagramConversationState)

# --- Add Debug Nodes ---
graph.add_node("insta_debug_before", insta_debug_before)
graph.add_node("insta_debug_after", insta_debug_after)

# --- Add Core Nodes ---
graph.add_node("normalize_state", normalize_state)
graph.add_node("store_conversation", store_conversation)
graph.add_node("store_insta_session", instauser_session)
graph.add_node("analyze_intent", analyze_intent)
graph.add_node("ask_missing_info", ask_missing_info)
graph.add_node("fetch_pricing_rules", fetch_pricing_rules)
graph.add_node("pricing_negotiation", pricing_negotiation)
graph.add_node("manual_negotiation_required", manual_negotiation_required)
graph.add_node("finalize_negotiation", finalize_negotiation)
graph.add_node("generate_ai_reply", generate_ai_reply)
graph.add_node("send_reply", send_reply)
graph.add_node("handle_rejection", handle_rejection)

# --- Set Entry Point ---
graph.set_entry_point("insta_debug_before")


# --- Build Edges ---
graph.add_edge("insta_debug_before", "normalize_state")
graph.add_edge("normalize_state", "store_conversation")
graph.add_edge("store_conversation", "store_insta_session")
graph.add_edge("store_insta_session", "analyze_intent")
graph.add_edge("analyze_intent", "ask_missing_info")

graph.add_conditional_edges(
    "ask_missing_info",
    ask_missing_info_next,
    {
        "fetch_pricing_rules": "fetch_pricing_rules",
        "generate_ai_reply": "generate_ai_reply",
        "handle_rejection": "handle_rejection",
    },
)

graph.add_edge("fetch_pricing_rules", "pricing_negotiation")

graph.add_conditional_edges(
    "pricing_negotiation",
    pricing_negotiation_next,
    {
        "finalize_negotiation": "finalize_negotiation",
        "manual_negotiation_required": "manual_negotiation_required",
    },
)

graph.add_edge("manual_negotiation_required", "generate_ai_reply")
graph.add_edge("finalize_negotiation", "generate_ai_reply")
graph.add_edge("generate_ai_reply", "send_reply")
graph.add_edge("send_reply", "insta_debug_after")
graph.add_edge("insta_debug_after", END)

# --- Compile Graph ---
instagram_graph = graph.compile()
