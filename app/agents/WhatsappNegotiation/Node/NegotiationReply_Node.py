from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappMessageIntent,
    WhatsappNegotiationState,
)
from app.utils.printcolors import Colors


def generate_reply_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into generate_reply_node")
    print("--------------------------------")
    intent = state.get("intent")
    min_price = state.get("min_price") or 0

    if intent == WhatsappMessageIntent.INTEREST:
        state["final_reply"] = (
            f"Great to hear that 😊\n"
            f"Our minimum budget for this campaign starts at ${min_price:.2f}. "
            "Let us know if that works for you."
        )

    elif intent == WhatsappMessageIntent.NEGOTIATE:
        state["final_reply"] = (
            f"Thanks for sharing your thoughts.\n"
            f"We can start from ${min_price:.2f}. "
            "Would that be workable for you?"
        )

    elif intent == WhatsappMessageIntent.REJECT:
        state["final_reply"] = (
            "Thanks for letting us know. "
            "If anything changes in the future, feel free to reach out."
        )

    elif intent == WhatsappMessageIntent.QUESTION:
        state["final_reply"] = (
            f"Our minimum budget is ${min_price:.2f}. "
            "Happy to discuss deliverables and timelines as well."
        )

    else:
        state["final_reply"] = (
            "Could you please clarify your expectations so we can proceed?"
        )

    print(f"[generate_reply_node] Intent: {intent}, Reply: {state['final_reply']}")
    print(f"{Colors.CYAN} Exiting from generate_reply_node")
    print("--------------------------------")
    return state
