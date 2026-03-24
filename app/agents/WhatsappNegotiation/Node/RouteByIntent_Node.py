from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
    WhatsappMessageIntent,
)
from app.Schemas.instagram.negotiation_schema import NextAction


def route_by_intent(state: WhatsappNegotiationState):
    intent = state.get("intent", WhatsappMessageIntent.UNCLEAR)
    next_action = state.get("next_action")

    # 0) Deal already closed — e.g. "Thanks for the opportunity" / "Ok thank you" should get
    #    a friendly reply (generate_reply), not run accept_negotiation again.
    if state.get("negotiation_completed") or state.get("negotiation_status") == "agreed":
        return "generate_reply"

    # 1) If intent is explicit ACCEPT, close the deal (so "I agree" never goes to counter_offer).
    if intent == WhatsappMessageIntent.ACCEPT:
        return "accept_negotiation"

    # 2) Route by NextAction when available (higher priority)
    if next_action is not None:
        # Normalize to enum if it's coming through as a raw value
        try:
            na = (
                next_action
                if isinstance(next_action, NextAction)
                else NextAction(next_action)
            )
        except Exception:
            na = None

        if na is not None:
            # Question / clarification style actions
            if na in {
                NextAction.ANSWER_QUESTION,
                NextAction.GENERATE_CLARIFICATION,
                NextAction.ASK_INTEREST,
                NextAction.ASK_AVAILABILITY,
                NextAction.WAIT_OR_ACKNOWLEDGE,
            }:
                return "generate_reply"

            # Influencer accepted → close deal, do NOT send to counter_offer
            if na == NextAction.ACCEPT_NEGOTIATION:
                return "accept_negotiation"

            # Pricing / negotiation steps (ask rate / escalate only)
            if na in {
                NextAction.ASK_RATE,
                NextAction.ESCALATE_NEGOTIATION,
            }:
                if state.get("min_price") and state.get("max_price"):
                    return "counter_offer"
                else:
                    return "fetch_pricing"

            # Confirmation / details
            if na in {
                NextAction.CONFIRM_PRICING,
                NextAction.CONFIRM_DELIVERABLES,
                NextAction.CONFIRM_TIMELINE,
            }:
                return "confirm_details"

            # Terminal states
            if na == NextAction.REJECT_NEGOTIATION:
                return "reject_negotiation"
            if na == NextAction.CLOSE_CONVERSATION:
                return "close_conversation"

    # 3) Fallback: route by high-level intent
    if intent == WhatsappMessageIntent.REJECT:
        return "generate_reply"

    if intent in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
    ):
        if state.get("min_price") and state.get("max_price"):
            return "counter_offer"
        else:
            return "fetch_pricing"
    return "generate_reply"
