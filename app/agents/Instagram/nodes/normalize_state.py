from app.Schemas.instagram.negotiation_schema import InstagramConversationState


def normalize_state(state: dict) -> dict:
    return {
        **state,
        "history": state.get("history", []),
        "analysis": state.get("analysis", {}),
        "intent": state.get("intent", "unclear"),
        "final_reply": state.get("final_reply", ""),
        "negotiationStatus": state.get("negotiationStatus", "pending"),
        "influencerResponse": state.get(
            "influencerResponse",
            {
                "availability": None,
                "rate": None,
            },
        ),
        # 🔑 IMPORTANT
        "pricingRules": state.get(
            "pricingRules",
            {
                "minPrice": 0,
                "maxPrice": 0,
            },
        ),
    }
