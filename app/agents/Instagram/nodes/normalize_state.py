from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.Schemas.instagram.negotiation_schema import MessageIntent, NextAction
from app.db.connection import get_db


async def normalize_state(state: dict) -> InstagramConversationState:
    print("Entering into Node Normalize State")
    print("--------------------------------")
    db = get_db()
    existing_session = await db.get_collection("instagram_sessions").find_one(
        {"thread_id": state.get("thread_id")}
    )
    print("Existing Session: ", existing_session)
    print("--------------------------------")
    normalized = {
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
        "asked_questions": state.get("asked_questions", {"rate": False}),
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

    # Preload existing rate if stored
    if existing_session and existing_session.get("final_rate") is not None:
        normalized["influencer_response"]["rate"] = existing_session["final_rate"]
        normalized["final_rate"] = existing_session["final_rate"]
        normalized["negotiation_status"] = existing_session.get(
            "negotiation_status", normalized["negotiation_status"]
        )

    print("Exiting Normalize State")
    print("--------------------------------")
    print("Normalized State: ", normalized)
    print("--------------------------------")
    return normalized
