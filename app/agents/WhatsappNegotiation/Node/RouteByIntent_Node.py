from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
    WhatsappMessageIntent,
)
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def route_by_intent(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering route_by_intent")
    print("--------------------------------")

    intent = state.get("intent", WhatsappMessageIntent.UNCLEAR)
    next_action = state.get("next_action")
    print(f"{Colors.CYAN}Routing based on intent: {intent}, next_action: {next_action}")

    # 0) Deal already closed — e.g. "Thanks for the opportunity" / "Ok thank you" should get
    #    a friendly reply (generate_reply), not run accept_negotiation again.
    if state.get("negotiation_completed") or state.get("negotiation_status") == "agreed":
        print(f"{Colors.YELLOW}Deal already agreed → generate_reply (post-deal message)")
        return "generate_reply"

    # 1) If intent is explicit ACCEPT, close the deal (so "I agree" never goes to counter_offer).
    if intent == WhatsappMessageIntent.ACCEPT:
        print(f"{Colors.YELLOW}Intent is ACCEPT → accept_negotiation")
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
                print(f"{Colors.YELLOW}NextAction={na} → generate_reply")
                return "generate_reply"

            # Influencer accepted → close deal, do NOT send to counter_offer
            if na == NextAction.ACCEPT_NEGOTIATION:
                print(
                    f"{Colors.YELLOW}NextAction=ACCEPT_NEGOTIATION → accept_negotiation"
                )
                return "accept_negotiation"

            # Pricing / negotiation steps (ask rate / escalate only)
            if na in {
                NextAction.ASK_RATE,
                NextAction.ESCALATE_NEGOTIATION,
            }:
                if state.get("min_price") and state.get("max_price"):
                    print(f"{Colors.YELLOW}NextAction={na} → counter_offer (pricing present)")
                    return "counter_offer"
                else:
                    print(f"{Colors.YELLOW}NextAction={na} → fetch_pricing first (pricing missing)")
                    return "fetch_pricing"

            # Confirmation / details
            if na in {
                NextAction.CONFIRM_PRICING,
                NextAction.CONFIRM_DELIVERABLES,
                NextAction.CONFIRM_TIMELINE,
            }:
                print(f"{Colors.YELLOW}NextAction={na} → confirm_details")
                return "confirm_details"

            # Terminal states
            if na == NextAction.REJECT_NEGOTIATION:
                print(f"{Colors.YELLOW}NextAction={na} → reject_negotiation")
                return "reject_negotiation"
            if na == NextAction.CLOSE_CONVERSATION:
                print(f"{Colors.YELLOW}NextAction={na} → close_conversation")
                return "close_conversation"

    # 3) Fallback: route by high-level intent
    if intent == WhatsappMessageIntent.REJECT:
        print(f"{Colors.YELLOW}Intent is REJECT → generate_reply")
        return "generate_reply"

    if intent in (
        WhatsappMessageIntent.INTEREST,
        WhatsappMessageIntent.NEGOTIATE,
        WhatsappMessageIntent.QUESTION,
    ):
        print(f"{Colors.CYAN}Intent is {intent} → price negotiation path")
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
