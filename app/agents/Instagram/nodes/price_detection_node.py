from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def pricing_decision(analysis, min_price, max_price):
    """
    Decide what to do next based on influencer's budget.
    """
    if not analysis.pricing_mentioned:
        return "ASK_PRICE"

    price = analysis.budget_amount

    if price < min_price:
        return "COUNTER_UP"
    elif price > max_price:
        return "COUNTER_DOWN"
    else:
        return "ACCEPT"


async def node_pricing_decision(
    state: InstagramConversationState,
) -> InstagramConversationState:
    """
    Node to update negotiation strategy/next_action in state.
    """
    decision = pricing_decision(state.analysis, state.min_price, state.max_price)
    state.next_action = decision
    state.strategy = decision
    return state
