from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    try:
        print(f"{Colors.GREEN}Entering into route_after_pricing")
        print("--------------------------------")
        print(f"Intent: {state.get('intent')}")
        print(f"Next Action: {state.get('next_action')}")
        print("--------------------------------")

        next_action = state.get("next_action")
        if next_action == NextAction.ESCALATE_NEGOTIATION:
            return "price_escalation"

        if next_action == NextAction.ACCEPT_NEGOTIATION:
            return "accept_negotiation"

        if next_action == NextAction.REJECT_NEGOTIATION:
            return "reject_negotiation"

        if next_action == NextAction.ANSWER_QUESTION:
            return "generate_reply"

        if next_action in [
            NextAction.ASK_INTEREST,
            NextAction.ASK_RATE,
            NextAction.ASK_AVAILABILITY,
        ]:
            return "generate_reply"

        if next_action in [
            NextAction.CONFIRM_PRICING,
            NextAction.CONFIRM_DELIVERABLES,
            NextAction.CONFIRM_TIMELINE,
        ]:
            return "generate_reply"

        if next_action == NextAction.GENERATE_REJECTION:
            return "generate_reply"

        if next_action == NextAction.GENERATE_CLARIFICATION:
            return "generate_reply"

        if next_action == NextAction.CLOSE_CONVERSATION:
            return "close_conversation"

        if next_action == NextAction.WAIT_OR_ACKNOWLEDGE:
            return "generate_reply"

        print(f"{Colors.RED}Unknown NextAction → Fallback to generate_reply")
        print("--------------------------------")
        print(f"{Colors.YELLOW} Exiting from route_after_pricing")
        return "generate_reply"
    except Exception as e:
        print(f"{Colors.RED} Error in route_after_pricing: {e}")
        print("--------------------------------")
        return "generate_reply"
