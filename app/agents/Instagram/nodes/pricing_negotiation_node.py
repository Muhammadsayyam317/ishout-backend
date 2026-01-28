from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
    NegotiationStrategy,
)


def pricing_negotiation(state: InstagramConversationState):
    rate = state["influencerResponse"].get("rate")
    min_price = state["pricingRules"].get("minPrice", 0)
    max_price = state["pricingRules"].get("maxPrice", float("inf"))

    if rate is None:
        state["next_action"] = NextAction.CONFIRM_PRICING.value
        state["strategy"] = NegotiationStrategy.SOFT.value
        return state

    if rate < min_price or rate > max_price:
        state["negotiationStatus"] = "countered"
        state["next_action"] = NextAction.CONFIRM_PRICING.value
        state["strategy"] = NegotiationStrategy.VALUE_BASED.value
        return state

    state["negotiationStatus"] = "agreed"
    state["next_action"] = NextAction.CLOSE_NEGOTIATION.value
    state["strategy"] = NegotiationStrategy.SOFT.value
    return state
