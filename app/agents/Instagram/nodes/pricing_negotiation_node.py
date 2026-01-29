from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
    NegotiationStrategy,
)


def pricing_negotiation(state: InstagramConversationState):
    print("Entering Pricing Negotiation Node")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    response = state["influencer_response"]
    pricing = state["pricing_rules"]

    rate = response.get("rate")
    min_price = pricing.get("minPrice", 0)
    max_price = pricing.get("maxPrice", float("inf"))

    # Rate not provided yet
    if rate is None:
        state["next_action"] = NextAction.CONFIRM_PRICING
        state["strategy"] = NegotiationStrategy.SOFT
        return state

    # Rate outside allowed range
    if rate < min_price or rate > max_price:
        state["negotiation_status"] = "escalated"
        state["next_action"] = NextAction.CONFIRM_PRICING
        state["strategy"] = NegotiationStrategy.VALUE_BASED
        return state

    # Accept deal
    state["negotiation_status"] = "agreed"
    state["next_action"] = NextAction.ACCEPT_NEGOTIATION
    state["strategy"] = NegotiationStrategy.SOFT

    print("Exiting Pricing Negotiation Node")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
