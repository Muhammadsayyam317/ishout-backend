from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.agents.WhatsappNegotiation.Node.IntentClassifier_Node import intentclassifier
from app.agents.WhatsappNegotiation.Node.NegotiationReply_Node import (
    generate_reply_node,
)
from app.agents.WhatsappNegotiation.Node.PriceEscalation_Node import (
    price_escalation_node,
)
from app.agents.WhatsappNegotiation.Node.RouteByIntent_Node import route_by_intent
from app.agents.WhatsappNegotiation.Node.acceptNegotiation_Node import (
    accept_negotiation_node,
)
from app.agents.WhatsappNegotiation.Node.admintakeover_Node import admin_takeover_node
from app.agents.WhatsappNegotiation.Node.closeNegotiation_Node import (
    close_conversation_node,
)
from app.agents.WhatsappNegotiation.Node.confirmDetail_Node import confirm_details_node
from app.agents.WhatsappNegotiation.Node.counteroffer_Node import counter_offer_node
from app.agents.WhatsappNegotiation.Node.fetchInfluencerinfo_Node import (
    fetch_pricing_node,
)
from app.agents.WhatsappNegotiation.Node.rejectNegotiation_Node import (
    reject_negotiation_node,
)
from app.agents.WhatsappNegotiation.Node.routeafterpricing_Node import (
    route_after_pricing,
)
from app.agents.WhatsappNegotiation.Node.send_reply_Node import send_whatsapp_reply_node
from app.agents.WhatsappNegotiation.Node.completeNegotiation_Node import (
    complete_negotiation_node,
)
from langgraph.graph import StateGraph, END

graph = StateGraph(WhatsappNegotiationState)

# ------------------------
# Register Nodes
# ------------------------
graph.add_node("intentclassifier", intentclassifier)
graph.add_node("fetch_pricing", fetch_pricing_node)
graph.add_node("generate_reply", generate_reply_node)
graph.add_node("counter_offer", counter_offer_node)
graph.add_node("price_escalation", price_escalation_node)
graph.add_node("admin_takeover", admin_takeover_node)
graph.add_node("send_message", send_whatsapp_reply_node)
graph.add_node("accept_negotiation", accept_negotiation_node)
graph.add_node("reject_negotiation", reject_negotiation_node)
graph.add_node("close_conversation", close_conversation_node)
graph.add_node("confirm_details", confirm_details_node)
graph.add_node("complete_negotiation", complete_negotiation_node)

graph.set_entry_point("intentclassifier")

# ------------------------
# Intent Routing
# ------------------------
graph.add_conditional_edges(
    "intentclassifier",
    route_by_intent,
    {
        "fetch_pricing": "fetch_pricing",
        "generate_reply": "generate_reply",
    },
)

# ------------------------
# Pricing Routing
# ------------------------
graph.add_conditional_edges(
    "fetch_pricing",
    route_after_pricing,
    {
        "counter_offer": "counter_offer",
        "price_escalation": "price_escalation",
        "generate_reply": "generate_reply",
        "admin_takeover": "admin_takeover",
        "accept_negotiation": "accept_negotiation",
        "reject_negotiation": "reject_negotiation",
        "close_conversation": "close_conversation",
        "confirm_details": "confirm_details",
    },
)

# ------------------------
# Final Transitions / Flow
# ------------------------
graph.add_edge("counter_offer", "complete_negotiation")  # accepted counter → finalize
graph.add_edge("price_escalation", "send_message")  # escalate until max reached
graph.add_edge("generate_reply", "send_message")
graph.add_edge("confirm_details", "send_message")  # send confirmation
graph.add_edge(
    "accept_negotiation", "complete_negotiation"
)  # influencer agreed → finalize
graph.add_edge("reject_negotiation", "send_message")
graph.add_edge("close_conversation", "send_message")

graph.add_edge("admin_takeover", END)
graph.add_edge("send_message", END)
graph.add_edge("complete_negotiation", END)  # negotiation fully completed

# ------------------------
# Compile Graph
# ------------------------
whatsapp_negotiation_graph = graph.compile()
