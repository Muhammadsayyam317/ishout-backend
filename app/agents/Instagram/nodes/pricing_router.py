from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def route_pricing_outcome(state: InstagramConversationState):
    """
    Decide next node based on negotiation_status
    """
    status = state.get("negotiation_status")

    if status == "CONFIRMED":
        return "finalize_negotiation"

    if status == "MANUAL_REQUIRED":
        return "manual_negotiation_required"
    return "generate_ai_reply"
