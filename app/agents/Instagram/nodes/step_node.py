from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)


def route_next_step(state: InstagramConversationState) -> str:
    action = state["next_action"]

    if action in [
        NextAction.REJECT_NEGOTIATION,
        NextAction.GENERATE_REJECTION,
    ]:
        return "handle_rejection"

    if action in [
        NextAction.ASK_INTEREST,
        NextAction.ASK_AVAILABILITY,
        NextAction.ASK_RATE,
        NextAction.GENERATE_CLARIFICATION,
        NextAction.WAIT_OR_ACKNOWLEDGE,
    ]:
        return "generate_ai_reply"

    if action in [
        NextAction.CONFIRM_PRICING,
        NextAction.ESCALATE_NEGOTIATION,
    ]:
        return "fetch_pricing_rules"

    return "generate_ai_reply"
