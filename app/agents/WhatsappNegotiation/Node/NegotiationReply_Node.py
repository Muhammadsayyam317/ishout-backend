from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationState,
    WhatsappMessageIntent,
)
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def generate_reply_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into generate_reply_node")
    print("--------------------------------")
    intent = state.get("intent")
    min_price = state.get("min_price") or 0

    if intent == WhatsappMessageIntent.INTEREST:
        state["final_reply"] = (
            f"Great to hear that 😊\nOur budget for this campaign is ${min_price:.2f}. Let us know if that works for you."
        )
        state["next_action"] = NextAction.ASK_RATE

    elif intent == WhatsappMessageIntent.NEGOTIATE:
        last_offer = state.get("last_offered_price", min_price)
        state["final_reply"] = (
            f"Thanks for sharing your thoughts.\nWe can start from ${last_offer:.2f}. Would that be workable for you?"
        )
        state["next_action"] = NextAction.ASK_RATE

    elif intent == WhatsappMessageIntent.REJECT:
        state["final_reply"] = (
            "Thanks for letting us know. If anything changes in the future, feel free to reach out."
        )
        state["next_action"] = NextAction.CLOSE_CONVERSATION

    elif intent == WhatsappMessageIntent.QUESTION:
        state["final_reply"] = (
            f"Our budget for this campaign is ${min_price:.2f}. Happy to discuss deliverables and timelines as well."
        )
        state["next_action"] = NextAction.ANSWER_QUESTION

    elif intent == WhatsappMessageIntent.ACCEPT:
        state["final_reply"] = (
            f"Great to hear that 😊\nWe can start from ${min_price:.2f}. Would that be workable for you?"
        )
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION

    else:
        state["final_reply"] = (
            "Could you please clarify your expectations so we can proceed?"
        )
        state["next_action"] = NextAction.GENERATE_CLARIFICATION

    print(
        f"{Colors.CYAN}[generate_reply_node] Intent: {intent}, Reply: {state['final_reply']}"
    )
    print(f"{Colors.YELLOW} Exiting from generate_reply_node")
    print("--------------------------------")
    return state
