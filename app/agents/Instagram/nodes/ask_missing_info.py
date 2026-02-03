from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


async def ask_missing_info(state: InstagramConversationState):
    print("Entering into Node Ask Missing Info")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    responses = state["influencer_response"]
    intent = state.get("intent")

    # Handle intents
    if intent == "reject":
        print("Intent is reject")
        state["next_action"] = NextAction.REJECT_NEGOTIATION.value
        return state

    if intent == "unclear":
        print("Intent is unclear")
        state["next_action"] = NextAction.GENERATE_CLARIFICATION.value
        return state
    if intent == "wait_or_acknowledge":
        print("Intent is wait_or_acknowledge")
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE.value
        return state
    if not responses.get("interest"):
        print("Interest is missing")
        state["next_action"] = NextAction.ASK_INTEREST.value
        return state
    if not responses.get("availability"):
        print("Availability is missing")
        state["next_action"] = NextAction.ASK_AVAILABILITY.value
        return state

    if not responses.get("rate"):
        print("Rate is missing")
        state["next_action"] = NextAction.ASK_RATE.value
        return state

    state["next_action"] = NextAction.CONFIRM_PRICING.value
    print("Pricing check")
    print("Exiting from Node Ask Missing Info")
    return state


# --- Define Conditional Functions ---
def ask_missing_info_next(state: InstagramConversationState):
    action = state.get("next_action")
    if action == "fetch_pricing_rules":
        return "fetch_pricing_rules"
    elif action == "generate_ai_reply":
        return "generate_ai_reply"
    elif action == "reject_negotiation":
        return "handle_rejection"
    return "generate_ai_reply"  # default


def pricing_negotiation_next(state: InstagramConversationState):
    status = state.get("negotiation_status")
    if status == "CONFIRMED":
        return "finalize_negotiation"
    elif status == "MANUAL_REQUIRED":
        return "manual_negotiation_required"
    return "finalize_negotiation"
