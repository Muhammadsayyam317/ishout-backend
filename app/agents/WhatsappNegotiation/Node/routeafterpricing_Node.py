from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    intent = state.get("intent")
    next_action = state.get("next_action")

    if intent == "interest":
        state["negotiation_round"] = 0
        state["last_offered_price"] = None
        state["user_offer"] = None
        state["negotiation_status"] = "pending"

    negotiation_actions = {
        NextAction.ASK_RATE,
        NextAction.ESCALATE_NEGOTIATION,
        NextAction.ACCEPT_NEGOTIATION,
    }

    if next_action in negotiation_actions:
        return "counter_offer"

    mapping = {
        NextAction.ANSWER_QUESTION: "generate_reply",
        NextAction.CONFIRM_PRICING: "confirm_details",
        NextAction.CONFIRM_DELIVERABLES: "confirm_details",
        NextAction.CONFIRM_TIMELINE: "confirm_details",
        NextAction.REJECT_NEGOTIATION: "reject_negotiation",
        NextAction.CLOSE_CONVERSATION: "close_conversation",
    }

    if next_action in mapping:
        return mapping[next_action]

    print("[route_after_pricing] No matching action found → generate_reply")
    return "generate_reply"
