from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
    WhatsappMessageIntent,
)
from app.utils.printcolors import Colors


def route_by_intent(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering route_by_intent")
    print("--------------------------------")

    intent = state.get("intent", WhatsappMessageIntent.UNCLEAR)
    print(f"{Colors.CYAN}Routing based on intent: {intent}")

    if intent == WhatsappMessageIntent.REJECT:
        print(f"{Colors.YELLOW}Intent is REJECT → generate_reply")
        return "generate_reply"

    if state["intent"] in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
        WhatsappMessageIntent.ACCEPT,
    ):
        print(f"{Colors.YELLOW}Intent requires pricing → fetch_pricing")
        return "fetch_pricing"
    print(f"{Colors.RED}Intent unclear → generate_reply")
    return "generate_reply"
