from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


def handle_rejection(state: InstagramConversationState) -> InstagramConversationState:
    print("Entering into Node Handle Rejection")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    state["negotiation_status"] = "rejected"
    state["next_action"] = NextAction.CLOSE_CONVERSATION
    print("Exiting from Node Handle Rejection")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
