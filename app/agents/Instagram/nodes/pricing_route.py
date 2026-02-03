from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def pricing_route(state: InstagramConversationState):
    return state["negotiation_status"]
