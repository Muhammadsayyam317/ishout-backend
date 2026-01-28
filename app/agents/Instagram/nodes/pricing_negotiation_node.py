from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
    NegotiationStrategy,
)


async def pricing_negotiation_node(state: InstagramConversationState):
    print("Entering into Node Pricing Negotiation")
    rate = state.influencerResponse.get("rate")
    rules = state["pricingRules"]

    if not rate:
        state["next_action"] = NextAction.CONFIRM_PRICING.value
        state["strategy"] = NegotiationStrategy.SOFT
        return state

    min_price = rules.get("minPrice", 0)
    max_price = rules.get("maxPrice", float("inf"))

    if rate < min_price:
        state["negotiationStatus"] = "countered"
        state["next_action"] = NextAction.CONFIRM_PRICING.value
        state["strategy"] = NegotiationStrategy.VALUE_BASED
        return state

    # Rate above max
    if rate > max_price:
        state["negotiationStatus"] = "countered"
        state["next_action"] = NextAction.CONFIRM_PRICING.value
        state["strategy"] = NegotiationStrategy.VALUE_BASED
        return state

    # Rate within range → accept deal
    state["negotiationStatus"] = "agreed"
    state["next_action"] = NextAction.CLOSE_NEGOTIATION.value
    state["strategy"] = NegotiationStrategy.SOFT
    return state
