from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)


async def fetch_pricing_rules(state: InstagramConversationState):
    details = state["influencer_details"]

    state["pricingRules"] = {
        "minPrice": details["min_price"],
        "maxPrice": details["max_price"],
    }

    state["negotiationStatus"] = "pending"
    return state
