from langgraph.graph import StateGraph
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.analyzes_message import node_analyze_message
from app.agents.Instagram.nodes.influencers_details_node import influencers_details_node
from app.agents.Instagram.nodes.generate_reply import node_generate_reply
from app.agents.Instagram.nodes.Send_reply_node import send_instagram_reply

graph = StateGraph(InstagramConversationState)

graph.add_node("analyze", node_analyze_message)
graph.add_node("influencer_details", influencers_details_node)
graph.add_node("generate", node_generate_reply)
graph.add_node("send", send_instagram_reply)

graph.set_entry_point("analyze")

# Edges
graph.add_edge("analyze", "influencer_details")
graph.add_edge("influencer_details", "generate")
graph.add_edge("generate", "send")

instagram_graph = graph.compile()


# graph.add_node("analyze", node_analyze_message)
# graph.add_node("decide_next", node_decide_next_step)
# graph.add_node("decide_price", node_pricing_decision)
# graph.add_node("influencer_details", influencers_details_node)
# graph.add_node("generate", node_generate_reply)
# graph.add_node("send", send_instagram_reply)

# graph.set_entry_point("analyze")

# graph.add_edge("analyze", "decide_next")
# graph.add_edge("decide_next", "decide_price")
# graph.add_edge("decide_price", "influencer_details")
# graph.add_edge("influencer_details", "generate")
# graph.add_edge("generate", "send")

# instagram_graph = graph.compile()
