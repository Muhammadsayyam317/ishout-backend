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
from langgraph.graph import StateGraph, START, END

negotiation_graph = StateGraph(WhatsappNegotiationState)

negotiation_graph.add_node("intentclassifier", intentclassifier)
negotiation_graph.add_node("fetch_pricing", fetch_pricing_node)
negotiation_graph.add_node("generate_reply", generate_reply_node)
negotiation_graph.add_node("counter_offer", counter_offer_node)
negotiation_graph.add_node("price_escalation", price_escalation_node)
negotiation_graph.add_node("admin_takeover", admin_takeover_node)
negotiation_graph.add_node("send_message", send_whatsapp_reply_node)
negotiation_graph.add_node("accept_negotiation", accept_negotiation_node)
negotiation_graph.add_node("reject_negotiation", reject_negotiation_node)
negotiation_graph.add_node("close_conversation", close_conversation_node)
negotiation_graph.add_node("confirm_details", confirm_details_node)
negotiation_graph.add_node("complete_negotiation", complete_negotiation_node)


negotiation_graph.add_edge(START, "intentclassifier")

# ----------------------
# Conditional routing from intent classifier
# ----------------------
negotiation_graph.add_conditional_edges(
    "intentclassifier",
    route_by_intent,
    {
        "fetch_pricing": "fetch_pricing",
        "generate_reply": "generate_reply",
    },
)

# ----------------------
# Conditional routing after pricing
# ----------------------
negotiation_graph.add_conditional_edges(
    "fetch_pricing",
    route_after_pricing,
    {
        "counter_offer": "counter_offer",
        "price_escalation": "price_escalation",
        "accept_negotiation": "accept_negotiation",
        "generate_reply": "generate_reply",
        "admin_takeover": "admin_takeover",
        "reject_negotiation": "reject_negotiation",
        "close_conversation": "close_conversation",
        "confirm_details": "confirm_details",
    },
)

negotiation_graph.add_edge(
    "counter_offer", "price_escalation"
)  # escalate after counter-offer
negotiation_graph.add_edge("price_escalation", "send_message")
negotiation_graph.add_edge("generate_reply", "send_message")
negotiation_graph.add_edge("confirm_details", "send_message")
negotiation_graph.add_edge("accept_negotiation", "complete_negotiation")
negotiation_graph.add_edge("reject_negotiation", "send_message")
negotiation_graph.add_edge("close_conversation", "send_message")

# ----------------------
# Admin takeover or end nodes
# ----------------------
negotiation_graph.add_edge("admin_takeover", END)
negotiation_graph.add_edge("send_message", END)
negotiation_graph.add_edge("complete_negotiation", END)
