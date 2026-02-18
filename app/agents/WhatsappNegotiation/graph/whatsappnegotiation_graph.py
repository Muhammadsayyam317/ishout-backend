from langgraph.graph import StateGraph, START, END
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.agents.WhatsappNegotiation.Node.IntentClassifier_Node import intentclassifier
from app.agents.WhatsappNegotiation.Node.RouteByIntent_Node import route_by_intent
from app.agents.WhatsappNegotiation.Node.fetchPricing_Node import fetch_pricing_node
from app.agents.WhatsappNegotiation.Node.counteroffer_Node import counter_offer_node
from app.agents.WhatsappNegotiation.Node.NegotiationReply_Node import (
    generate_reply_node,
)
from app.agents.WhatsappNegotiation.Node.acceptNegotiation_Node import (
    accept_negotiation_node,
)
from app.agents.WhatsappNegotiation.Node.rejectNegotiation_Node import (
    reject_negotiation_node,
)
from app.agents.WhatsappNegotiation.Node.closeNegotiation_Node import (
    close_conversation_node,
)
from app.agents.WhatsappNegotiation.Node.confirmDetail_Node import confirm_details_node
from app.agents.WhatsappNegotiation.Node.completeNegotiation_Node import (
    complete_negotiation_node,
)
from app.agents.WhatsappNegotiation.Node.admintakeover_Node import admin_takeover_node
from app.agents.WhatsappNegotiation.Node.send_reply_Node import send_whatsapp_reply_node
from app.utils.custom_logging import (
    whatsapp_negotiation_debug_before,
    whatsapp_negotiation_debug_after,
)

# ----------------------
# Graph Initialization
# ----------------------
negotiation_graph = StateGraph(WhatsappNegotiationState)

# ----------------------
# Register Nodes
# ----------------------
negotiation_graph.add_node("negotiatedebug_before", whatsapp_negotiation_debug_before)
negotiation_graph.add_node("negotiatedebug_after", whatsapp_negotiation_debug_after)

negotiation_graph.add_node("intentclassifier", intentclassifier)
negotiation_graph.add_node("fetch_pricing", fetch_pricing_node)
negotiation_graph.add_node("counter_offer", counter_offer_node)
negotiation_graph.add_node("generate_reply", generate_reply_node)
negotiation_graph.add_node("accept_negotiation", accept_negotiation_node)
negotiation_graph.add_node("reject_negotiation", reject_negotiation_node)
negotiation_graph.add_node("close_conversation", close_conversation_node)
negotiation_graph.add_node("confirm_details", confirm_details_node)
negotiation_graph.add_node("complete_negotiation", complete_negotiation_node)
negotiation_graph.add_node("admin_takeover", admin_takeover_node)
negotiation_graph.add_node("send_message", send_whatsapp_reply_node)

negotiation_graph.add_edge(START, "negotiatedebug_before")
negotiation_graph.add_edge("negotiatedebug_before", "intentclassifier")

negotiation_graph.add_conditional_edges(
    "intentclassifier",
    route_by_intent,
    {
        "fetch_pricing": "fetch_pricing",
        "counter_offer": "counter_offer",
        "generate_reply": "generate_reply",
        "accept_negotiation": "accept_negotiation",
        "reject_negotiation": "reject_negotiation",
        "close_conversation": "close_conversation",
        "confirm_details": "confirm_details",
        "admin_takeover": "admin_takeover",
    },
)

# After fetching pricing → always go to counter_offer
negotiation_graph.add_conditional_edges(
    "fetch_pricing",
    lambda state: "counter_offer",
    {"counter_offer": "counter_offer"},
)

# ==========================================================
# BUSINESS LOGIC → DEBUG AFTER
# ==========================================================
negotiation_graph.add_edge("counter_offer", "negotiatedebug_after")
negotiation_graph.add_edge("generate_reply", "negotiatedebug_after")
negotiation_graph.add_edge("confirm_details", "negotiatedebug_after")
negotiation_graph.add_edge("reject_negotiation", "negotiatedebug_after")
negotiation_graph.add_edge("close_conversation", "negotiatedebug_after")
negotiation_graph.add_edge("accept_negotiation", "negotiatedebug_after")
negotiation_graph.add_edge("complete_negotiation", "negotiatedebug_after")

negotiation_graph.add_edge("negotiatedebug_after", "send_message")

negotiation_graph.add_edge("send_message", END)
negotiation_graph.add_edge("admin_takeover", END)
whatsapp_negotiation_agent = negotiation_graph.compile()
