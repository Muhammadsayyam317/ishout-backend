from app.agents.Instagram.state.influencer_details_state import (
    InstagramConversationState,
)


def normalize_state(state: InstagramConversationState) -> InstagramConversationState:
    state = dict(state)
    print(type(state), state)

    return {
        **state,
        "askedQuestions": state.get("askedQuestions")
        or {
            "rate": False,
            "availability": False,
            "interest": False,
        },
        "influencerResponse": state.get("influencerResponse")
        or {
            "rate": None,
            "availability": None,
            "interest": None,
        },
        "pricingRules": state.get("pricingRules")
        or {
            "minPrice": 0.0,
            "maxPrice": 0.0,
        },
        "negotiationStatus": state.get("negotiationStatus", "pending"),
        "history": state.get("history") or [],
        "final_reply": state.get("final_reply", ""),
        "next_action": state.get("next_action", ""),
        "analysis": state.get("analysis") or {},
        "intent": state.get("intent", "unclear"),
        "lastMessage": state.get("lastMessage", ""),
    }
