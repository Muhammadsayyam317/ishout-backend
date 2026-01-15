from langgraph.graph import StateGraph
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.agents.Instagram.nodes.Send_reply_node import send_instagram_reply
from app.agents.Instagram.nodes.analyzes_message import node_analyze_message
from app.agents.Instagram.nodes.generate_reply import generate_reply_node


graph = StateGraph(InstagramConversationState)


graph.add_node("analyze_message", node_analyze_message)
graph.add_node("generate_reply", generate_reply_node)
graph.add_node("send_reply", send_instagram_reply)

graph.set_entry_point("analyze_message")
graph.add_edge("analyze_message", "generate_reply")
graph.add_edge("generate_reply", "send_reply")

instagram_graph = graph.compile()
