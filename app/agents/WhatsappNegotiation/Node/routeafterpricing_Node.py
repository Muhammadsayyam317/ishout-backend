from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into route_after_pricing")
    print("--------------------------------")
    print(f"{Colors.CYAN}Routing after pricing: {state['intent']}")
    print("--------------------------------")

    if state["intent"] == WhatsappMessageIntent.NEGOTIATE:
        return "counter_offer"

    if state["intent"] == WhatsappMessageIntent.ACCEPT:
        return "generate_reply"

    if state["intent"] == WhatsappMessageIntent.QUESTION:
        return "generate_reply"

    if state["intent"] == WhatsappMessageIntent.INTEREST:
        return "generate_reply"
    print(f"{Colors.CYAN}Exiting from route_after_pricing")
    print("--------------------------------")

    return "generate_reply"
