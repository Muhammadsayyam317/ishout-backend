from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


def pricing_negotiation(state: InstagramConversationState):
    state.setdefault("negotiation_status", "PENDING")

    rate = state["influencer_response"].get("rate")
    min_price = state["pricing_rules"]["minPrice"]
    max_price = state["pricing_rules"]["maxPrice"]

    if rate is None:
        state["next_action"] = NextAction.ASK_RATE
        return state

    if min_price <= rate <= max_price:
        state["negotiation_status"] = "CONFIRMED"
        state["final_rate"] = rate
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION
    else:
        state["negotiation_status"] = "MANUAL_REQUIRED"
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION
        return state

    state["negotiation_status"] = "MANUAL_REQUIRED"
    return state
