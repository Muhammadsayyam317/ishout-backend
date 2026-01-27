from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)


def normalize_state(state: InstagramConversationState) -> InstagramConversationState:
    return {
        **state,
        # Question tracking
        "askedQuestions": state.get("askedQuestions")
        or {
            "rate": False,
            "availability": False,
            "interest": False,
        },
        # Influencer replies
        "influencerResponse": state.get("influencerResponse")
        or {
            "rate": None,
            "availability": None,
            "interest": None,
        },
        # Pricing rules
        "pricingRules": state.get("pricingRules")
        or {
            "minPrice": 0.0,
            "maxPrice": 0.0,
        },
        # Negotiation state
        "negotiationStatus": state.get("negotiationStatus", "pending"),
        # History
        "history": state.get("history") or [],
        # Defaults
        "final_reply": state.get("final_reply", ""),
        "next_action": state.get("next_action", ""),
        "analysis": state.get("analysis") or {},
        "intent": state.get("intent", "unclear"),
        "lastMessage": state.get("lastMessage", ""),
    }
