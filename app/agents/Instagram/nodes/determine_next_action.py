from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    MessageIntent,
    NextAction,
)


def determine_next_action(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("Entering into Node Determine Next Action")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    analysis = state["analysis"]

    # Rejection intent
    if analysis["intent"] == MessageIntent.REJECT:
        state["next_action"] = NextAction.GENERATE_REJECTION
        state["negotiation_status"] = "rejected"
        return state

    missing = analysis["missing_required_details"]

    if "interest" in missing:
        state["next_action"] = NextAction.ASK_INTEREST
        return state

    if "availability" in missing:
        state["next_action"] = NextAction.ASK_AVAILABILITY
        return state

    if "rate" in missing:
        state["next_action"] = NextAction.ASK_RATE
        return state

    # Everything available
    state["next_action"] = NextAction.CONFIRM_PRICING
    print("Exiting from Node Determine Next Action")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
