from langgraph.graph import StateGraph
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.reject_price_node import manual_negotiation_required
from app.agents.Instagram.nodes.store_conversation_node import store_conversation
from nodes.normalize_state import normalize_state
from nodes.analyzes_intent import analyze_intent
from nodes.determine_next_action import determine_next_action
from nodes.finalize_negotiation import finalize_negotiation
from nodes.generate_ai_reply import generate_ai_reply
from app.agents.Instagram.nodes.fetch_influencer_price_node import fetch_pricing_rules
from app.agents.Instagram.nodes.pricing_negotiation_node import pricing_negotiation
from app.agents.Instagram.nodes.Send_reply_node import send_reply

instagram_graph = StateGraph(InstagramConversationState)
instagram_graph.set_entry_point("normalize_state")

instagram_graph.add_node("normalize_state", normalize_state)
instagram_graph.add_node("store_conversation", store_conversation)
instagram_graph.add_node("analyze_intent", analyze_intent)
instagram_graph.add_node("determine_next_action", determine_next_action)
instagram_graph.add_node("fetch_pricing_rules", fetch_pricing_rules)
instagram_graph.add_node("pricing_negotiation", pricing_negotiation)
instagram_graph.add_node("manual_negotiation_required", manual_negotiation_required)
instagram_graph.add_node("finalize_negotiation", finalize_negotiation)
instagram_graph.add_node("generate_ai_reply", generate_ai_reply)
instagram_graph.add_node("send_reply", send_reply)

instagram_graph.add_edge("normalize_state", "store_conversation")
instagram_graph.add_edge("store_conversation", "analyze_intent")
instagram_graph.add_edge("analyze_intent", "determine_next_action")
instagram_graph.add_edge("determine_next_action", "fetch_pricing_rules")
instagram_graph.add_edge("fetch_pricing_rules", "pricing_negotiation")
instagram_graph.add_edge("pricing_negotiation", "manual_negotiation_required")
instagram_graph.add_edge("manual_negotiation_required", "finalize_negotiation")
instagram_graph.add_edge("finalize_negotiation", "generate_ai_reply")
instagram_graph.add_edge("generate_ai_reply", "send_reply")

instagram_graph = instagram_graph.compile()
