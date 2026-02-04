from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.Schemas.instagram.negotiation_schema import MessageIntent, NextAction


def normalize_state(state: dict) -> InstagramConversationState:
    print("Entering into Node Normalize State")
    print("--------------------------------")
    return {
        # identifiers
        "thread_id": state.get("thread_id"),
        "convoId": state.get("convoId"),
        "campaign_id": state.get("campaign_id"),
        "influencer_id": state.get("influencer_id"),
        # messages
        "user_message": state.get("user_message", ""),
        "last_message": state.get("last_message", ""),
        "history": state.get("history", []),
        # intent + analysis
        "intent": state.get("intent", MessageIntent.UNCLEAR),
        "analysis": state.get("analysis", {}),
        # negotiation data
        "asked_questions": state.get(
            "asked_questions",
            {
                "rate": False,
            },
        ),
        "influencer_response": state.get(
            "influencer_response",
            {"rate": None, "interest": False, "availability": None},
        ),
        "pricing_rules": state.get(
            "pricing_rules",
            {
                "minPrice": 0,
                "maxPrice": 0,
            },
        ),
        # status
        "negotiation_status": state.get("negotiation_status", "pending"),
        "next_action": state.get("next_action", NextAction.WAIT_OR_ACKNOWLEDGE),
        "final_reply": state.get("final_reply", ""),
    }
