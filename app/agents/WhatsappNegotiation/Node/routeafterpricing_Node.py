from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering route_after_pricing")
    print("--------------------------------")

    intent = state.get("intent")
    next_action = state.get("next_action")

    # Reset immediately BEFORE anything else
    if intent == WhatsappMessageIntent.INTEREST:
        state["negotiation_round"] = 0
        state["last_offered_price"] = None
        state["user_offer"] = None
        state["negotiation_status"] = "pending"

    print(f"{Colors.CYAN}Intent: {intent} | NextAction: {next_action}")

    # Any negotiation-related action -> single engine
    negotiation_actions = {
        NextAction.ASK_RATE,
        NextAction.ESCALATE_NEGOTIATION,
        NextAction.ACCEPT_NEGOTIATION,
    }

    if next_action in negotiation_actions:
        print(f"{Colors.YELLOW}Routing to negotiation_engine")
        return "negotiation_engine"

    mapping = {
        NextAction.ANSWER_QUESTION: "generate_reply",
        NextAction.CONFIRM_PRICING: "confirm_details",
        NextAction.CONFIRM_DELIVERABLES: "confirm_details",
        NextAction.CONFIRM_TIMELINE: "confirm_details",
        NextAction.REJECT_NEGOTIATION: "reject_negotiation",
        NextAction.CLOSE_CONVERSATION: "close_conversation",
    }

    if next_action in mapping:
        print(f"{Colors.CYAN}Routed to: {mapping[next_action]}")
        return mapping[next_action]

    print(f"{Colors.RED}Fallback → generate_reply")
    return "generate_reply"
