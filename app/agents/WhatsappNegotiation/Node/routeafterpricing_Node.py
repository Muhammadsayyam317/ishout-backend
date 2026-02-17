from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
    WhatsappMessageIntent,
)
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering route_after_pricing")
    print("--------------------------------")
    intent = state.get("intent")
    next_action = state.get("next_action")
    print(f"{Colors.CYAN}Intent: {intent} | NextAction: {next_action}")

    if intent == WhatsappMessageIntent.INTEREST:
        state["negotiation_round"] = 0
        state["last_offered_price"] = None
        state["user_offer"] = None
        state["negotiation_status"] = "pending"
        print(f"{Colors.CYAN}Resetting negotiation state for INTEREST")

    if next_action == NextAction.ASK_RATE:
        return "counter_offer"
    print(f"{Colors.YELLOW}Routing to counter_offer")
    if next_action == NextAction.ESCALATE_NEGOTIATION:
        return "price_escalation"
    print(f"{Colors.YELLOW}Routing to price_escalation")
    if next_action == NextAction.ACCEPT_NEGOTIATION:
        return "accept_negotiation"
    print(f"{Colors.YELLOW}Routing to accept_negotiation")
    mapping = {
        NextAction.ANSWER_QUESTION: "generate_reply",
        NextAction.CONFIRM_PRICING: "confirm_details",
        NextAction.CONFIRM_DELIVERABLES: "confirm_details",
        NextAction.CONFIRM_TIMELINE: "confirm_details",
        NextAction.REJECT_NEGOTIATION: "reject_negotiation",
        NextAction.CLOSE_CONVERSATION: "close_conversation",
    }

    print(f"{Colors.CYAN}Routing to: {mapping.get(next_action, 'generate_reply')}")
    print(f"{Colors.YELLOW}Exiting route_after_pricing")
    print("--------------------------------")
    return mapping.get(next_action, "generate_reply")
