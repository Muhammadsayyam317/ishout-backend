from app.Schemas.instagram.negotiation_schema import InstagramConversationState


async def node_decide_next_step(
    state: InstagramConversationState,
) -> InstagramConversationState:
    """
    Decide what the AI should do next based on analysis.
    """
    if not state.analysis:
        state.next_action = "wait_or_acknowledge"
        return state

    state.next_action = state.analysis.recommended_next_action
    return state
