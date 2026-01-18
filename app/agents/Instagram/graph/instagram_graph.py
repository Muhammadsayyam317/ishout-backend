from langgraph.graph import StateGraph
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.analyzes_message import node_analyze_message
from app.agents.Instagram.nodes.price_detection_node import node_pricing_decision
from app.agents.Instagram.nodes.generate_reply import node_generate_reply
from app.agents.Instagram.nodes.Send_reply_node import send_instagram_reply

graph = StateGraph(InstagramConversationState)

# Nodes
graph.add_node("analyze", node_analyze_message)
graph.add_node("decide_price", node_pricing_decision)
graph.add_node("generate", node_generate_reply)
graph.add_node("send", send_instagram_reply)

# Flow
graph.set_entry_point("analyze")
graph.add_edge("analyze", "decide_price")
graph.add_edge("decide_price", "generate")
graph.add_edge("generate", "send")

instagram_graph = graph.compile()
