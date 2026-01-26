from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)


async def normalize_state(state: InstagramConversationState):
    if state.askedQuestions is None:
        state.askedQuestions = {}

    if state.influencerResponse is None:
        state.influencerResponse = {}

    if state.pricingRules is None:
        state.pricingRules = {}

    if state.history is None:
        state.history = []

    state.lastMessage = state.user_message
    state.history.append(state.user_message)

    # migrate legacy fields
    if state.rate is not None:
        state.influencerResponse["rate"] = state.rate

    if state.availability:
        state.influencerResponse["availability"] = state.availability

    if state.interest is not None:
        state.influencerResponse["interest"] = state.interest

    return state
