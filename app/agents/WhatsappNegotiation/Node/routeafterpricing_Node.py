from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def route_after_pricing(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into route_after_pricing")
    print("--------------------------------")
    print(f"Intent: {state.get('intent')}")
    print(f"Next Action: {state.get('next_action')}")
    print("--------------------------------")

    next_action = state.get("next_action")
    # 🔥 1. ESCALATION (Highest Priority)
    if next_action == NextAction.ESCALATE_NEGOTIATION:
        return "price_escalation_node"

    # ✅ 2. ACCEPT NEGOTIATION
    if next_action == NextAction.ACCEPT_NEGOTIATION:
        return "accept_negotiation_node"

    # ❌ 3. REJECT NEGOTIATION
    if next_action == NextAction.REJECT_NEGOTIATION:
        return "reject_negotiation_node"

    # 💬 4. ANSWER QUESTION
    if next_action == NextAction.ANSWER_QUESTION:
        return "generate_reply"

    # 🧠 5. ASKING FLOW
    if next_action in [
        NextAction.ASK_INTEREST,
        NextAction.ASK_RATE,
        NextAction.ASK_AVAILABILITY,
    ]:
        return "generate_reply"

    # 📦 6. CONFIRMATION FLOW
    if next_action in [
        NextAction.CONFIRM_PRICING,
        NextAction.CONFIRM_DELIVERABLES,
        NextAction.CONFIRM_TIMELINE,
    ]:
        return "generate_reply"

    # 🚫 7. GENERATE REJECTION
    if next_action == NextAction.GENERATE_REJECTION:
        return "generate_reply"

    # 🧹 8. CLARIFICATION
    if next_action == NextAction.GENERATE_CLARIFICATION:
        return "generate_reply"

    # 👋 9. CLOSE CONVERSATION
    if next_action == NextAction.CLOSE_CONVERSATION:
        return "close_conversation_node"

    # ⏳ 10. WAIT / ACK
    if next_action == NextAction.WAIT_OR_ACKNOWLEDGE:
        return "generate_reply"

    # 🛑 Fallback (Never break the system)
    print(f"{Colors.RED}Unknown NextAction → Fallback to generate_reply")
    return "generate_reply"
