from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into route_after_pricing")
    print("--------------------------------")

    next_action = state.get("next_action")
    negotiation_status = state.get("negotiation_status", "pending")
    negotiation_round = state.get("negotiation_round", 0)
    last_offered_price = state.get("last_offered_price")

    print(
        f"{Colors.CYAN} NextAction: {next_action} | "
        f"Round: {negotiation_round} | "
        f"Status: {negotiation_status}"
    )

    if next_action == NextAction.ASK_RATE:
        if negotiation_round == 0 or not last_offered_price:
            print(f"{Colors.YELLOW} First offer → generate_reply")
            return "generate_reply"

        print(f"{Colors.YELLOW} Ongoing negotiation → price_escalation")
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

    if next_action in mapping:
        print(f"{Colors.CYAN} Routed to: {mapping[next_action]}")
        return mapping[next_action]

    print(f"{Colors.RED} Unknown NextAction → Fallback to generate_reply")
    print("--------------------------------")

    return "generate_reply"
