from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NegotiationStrategy,
)


def pricing_decision(analysis, min_price, max_price):
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
    decision = pricing_decision(
        state.analysis,
        state.min_price,
        state.max_price,
    )
    state.next_action = decision
    STRATEGY_MAP = {
        "ASK_PRICE": NegotiationStrategy.SOFT,
        "COUNTER_UP": NegotiationStrategy.VALUE_BASED,
        "COUNTER_DOWN": NegotiationStrategy.VALUE_BASED,
        "ACCEPT": NegotiationStrategy.SOFT,
    }
    state.strategy = STRATEGY_MAP.get(decision, NegotiationStrategy.SOFT)
    return state
