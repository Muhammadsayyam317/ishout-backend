from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def normalize_state(state: dict) -> InstagramConversationState:
    """Initialize state with defaults if missing."""
    return {
        **state,
        "history": state.get("history", []),
        "analysis": state.get("analysis", {}),
        "intent": state.get("intent", "unclear"),
        "final_reply": state.get("final_reply", ""),
        "negotiationStatus": state.get("negotiationStatus", "pending"),
        "askedQuestions": state.get("askedQuestions", {}),
        "influencerResponse": state.get(
            "influencerResponse",
            {"availability": None, "rate": None, "interest": None},
        ),
        "pricingRules": state.get("pricingRules", {"minPrice": 0, "maxPrice": 0}),
        "next_action": state.get("next_action", "wait_or_acknowledge"),
    }
