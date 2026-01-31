from app.Schemas.instagram.negotiation_schema import InstagramConversationState


async def node_decide_next_step(
    state: InstagramConversationState,
) -> InstagramConversationState:

    print("Entering into Node Decide Next Step")
    if not state.analysis:
        print("No analysis found")
        state.next_action = "wait_or_acknowledge"
        return state

    state.next_action = state.analysis.recommended_next_action
    print(f"Next action: {state.next_action}")
    print("Exiting from Node Decide Next Step")
    return state
