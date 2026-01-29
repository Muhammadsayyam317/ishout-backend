from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def accept_offer(state: InstagramConversationState):
    state["negotiation_status"] = "agreed"
    return state
