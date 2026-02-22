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

    if intent == WhatsappMessageIntent.ACCEPT:
        print(f"{Colors.YELLOW}Intent is ACCEPT → accept_negotiation")
        return "accept_negotiation"

    if intent in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
    ):
        print(f"{Colors.CYAN}Intent is {intent} → proceed to counter_offer")
        if state.get("min_price") and state.get("max_price"):
            print(f"{Colors.CYAN}Pricing already present → proceed to counter_offer")
            return "counter_offer"
        else:
            print(f"{Colors.CYAN}Pricing missing → fetch_pricing first")
            return "fetch_pricing"
    print(f"{Colors.RED}No matching action found → generate_reply")
    print("--------------------------------")
    print(f"{Colors.YELLOW}Exiting route_by_intent")
    return "generate_reply"
