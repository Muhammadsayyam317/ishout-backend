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

    if intent == WhatsappMessageIntent.REJECT:
        state["final_reply"] = (
            "Thanks for letting us know. "
            "If anything changes in the future, feel free to reach out."
        )
        state["next_action"] = NextAction.CLOSE_CONVERSATION

    elif intent == WhatsappMessageIntent.QUESTION:
        state["final_reply"] = (
            "Happy to clarify! Let us know what details you’d like about "
            "deliverables or timelines."
        )
        state["next_action"] = NextAction.ANSWER_QUESTION

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
