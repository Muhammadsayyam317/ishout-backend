from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into route_after_pricing")
    print("--------------------------------")
    next_action = state.get("next_action")
    negotiation_status = state.get("negotiation_status", "pending")

    # Multi-round negotiation routing
    if next_action == NextAction.ASK_RATE and negotiation_status in [
        "pending",
        "escalated",
    ]:
        print(f"{Colors.CYAN} [route_after_pricing] NextAction: {next_action}")
        return "price_escalation"
    mapping = {
        NextAction.ESCALATE_NEGOTIATION: "price_escalation",
        NextAction.ACCEPT_NEGOTIATION: "accept_negotiation",
        NextAction.REJECT_NEGOTIATION: "reject_negotiation",
        NextAction.ANSWER_QUESTION: "generate_reply",
        NextAction.CONFIRM_PRICING: "confirm_details",
        NextAction.CONFIRM_DELIVERABLES: "confirm_details",
        NextAction.CONFIRM_TIMELINE: "confirm_details",
        NextAction.CLOSE_CONVERSATION: "close_conversation",
    }
    print(f"{Colors.CYAN} [route_after_pricing] Mapping: {mapping}")
    if next_action in mapping:
        print(
            f"{Colors.CYAN} [route_after_pricing] NextAction in mapping: {next_action}"
        )
        return mapping[next_action]
    print(
        f"{Colors.RED} [route_after_pricing] Unknown NextAction → Fallback to generate_reply"
    )
    print(f"{Colors.YELLOW} Exiting from route_after_pricing")
    print("--------------------------------")
    return "generate_reply"
