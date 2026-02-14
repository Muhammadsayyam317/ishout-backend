from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors


def route_by_intent(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into route_by_intent")
    print("--------------------------------")
    print(f"{Colors.CYAN}Routing by intent: {state['intent']}")
    print("--------------------------------")
    if state["intent"] == WhatsappMessageIntent.REJECT:
        return "generate_reply"

    if state["intent"] in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
        WhatsappMessageIntent.ACCEPT,
    ):
        print(f"{Colors.CYAN}Fetching pricing for campaign influencer: {state['_id']}")
        print("--------------------------------")
        return "fetch_pricing"

    print(f"{Colors.CYAN}Exiting from route_by_intent")
    print("--------------------------------")
    return "generate_reply"
