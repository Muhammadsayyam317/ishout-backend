from langgraph.graph import StateGraph
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.Send_reply_node import send_instagram_reply
from app.agents.Instagram.nodes.fetch_influencer_price_node import fetch_pricing_rules
from app.agents.Instagram.nodes.generate_ai_reply import generate_ai_reply
from app.agents.Instagram.nodes.normalize_state import normalize_state
from app.agents.Instagram.nodes.analyzes_intent import analyze_intent
from app.agents.Instagram.nodes.ask_missing_info import ask_missing_info
from app.agents.Instagram.nodes.pricing_negotiation_node import pricing_negotiation_node
from app.agents.Instagram.nodes.reject_price_node import manual_negotiation_required
from app.agents.Instagram.nodes.store_influencer_details import store_influencer_details


instagram_graph = StateGraph(InstagramConversationState)


instagram_graph.set_entry_point("normalize_state")

# Add nodes
instagram_graph.add_node("normalize_state", normalize_state)
instagram_graph.add_node("store_influencer_details", store_influencer_details)
instagram_graph.add_node("analyze_intent", analyze_intent)
instagram_graph.add_node("ask_missing_info", ask_missing_info)
instagram_graph.add_node("fetch_pricing_rules", fetch_pricing_rules)
instagram_graph.add_node("pricing_negotiation", pricing_negotiation_node)
instagram_graph.add_node("manual_negotiation", manual_negotiation_required)
instagram_graph.add_node("generate_ai_reply", generate_ai_reply)
instagram_graph.add_node("send_reply", send_instagram_reply)

# ---------------- Edges ----------------
# Sequential flow
instagram_graph.add_edge("normalize_state", "store_influencer_details")
instagram_graph.add_edge("store_influencer_details", "analyze_intent")
instagram_graph.add_edge("analyze_intent", "ask_missing_info")
instagram_graph.add_edge("ask_missing_info", "fetch_pricing_rules")
instagram_graph.add_edge("fetch_pricing_rules", "pricing_negotiation")
instagram_graph.add_edge("pricing_negotiation", "manual_negotiation")
instagram_graph.add_edge("pricing_negotiation", "store_influencer_details")
instagram_graph.add_edge("manual_negotiation", "store_influencer_details")
instagram_graph.add_edge("store_influencer_details", "generate_ai_reply")
instagram_graph.add_edge("generate_ai_reply", "send_reply")

# Compile
instagram_graph = instagram_graph.compile()
