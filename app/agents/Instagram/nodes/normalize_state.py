from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)


async def normalize_state(state: InstagramConversationState):
    state.setdefault("askedQuestions", {})
    state.setdefault("influencerResponse", {})
    state.setdefault("pricingRules", {})
    state.setdefault("history", [])

    state["lastMessage"] = state["user_message"]
    state["history"].append(state["user_message"])

    # Stop using state.rate / availability / interest
    if state.get("rate") is not None:
        state["influencerResponse"]["rate"] = state["rate"]

    if state.get("availability"):
        state["influencerResponse"]["availability"] = state["availability"]

    if state.get("interest") is not None:
        state["influencerResponse"]["interest"] = state["interest"]

    return state
