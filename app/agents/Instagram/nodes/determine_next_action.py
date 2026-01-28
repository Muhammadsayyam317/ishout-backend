from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


def determine_next_action(state: InstagramConversationState):
    """Check missing info and route to the proper next action."""
    responses = state["influencerResponse"]

    if state["intent"] == "reject":
        state["next_action"] = NextAction.REJECT_NEGOTIATION.value
        return state

    if not responses.get("interest"):
        state["next_action"] = NextAction.ASK_INTEREST.value
        return state

    if not responses.get("availability"):
        state["next_action"] = NextAction.ASK_AVAILABILITY.value
        return state

    if not responses.get("rate"):
        state["next_action"] = NextAction.ASK_RATE.value
        return state

    # If all required info provided
    state["next_action"] = NextAction.CONFIRM_PRICING.value
    return state
