from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors


def route_by_intent(state: WhatsappNegotiationState):
    print("Routing after pricing...")
    print(f"{Colors.GREEN}Entering into route_after_pricing")
    print("--------------------------------")
    print(f"{Colors.CYAN}Routing after pricing: {state['intent']}")
    print("--------------------------------")

    if state["intent"] == WhatsappMessageIntent.REJECT:
        return "generate_reply"

    if state["intent"] in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
        WhatsappMessageIntent.ACCEPT,
    ):
        return "fetch_pricing"

    print(f"{Colors.YELLOW}Exiting from route_after_pricing")
    print("--------------------------------")
    return "generate_reply"
