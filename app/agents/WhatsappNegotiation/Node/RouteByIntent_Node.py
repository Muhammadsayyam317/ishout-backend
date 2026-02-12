from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)


def route_by_intent(state: WhatsappNegotiationState):
    if state["intent"] == WhatsappMessageIntent.REJECT:
        return "generate_reply"

    if state["intent"] in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
    ):
        return "fetch_pricing"

    return "generate_reply"
