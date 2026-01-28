from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


def handle_rejection(state: InstagramConversationState) -> InstagramConversationState:
    state["negotiation_status"] = "rejected"
    state["next_action"] = NextAction.CLOSE_CONVERSATION
    return state
