from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def confirm_details_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering confirm_details_node")
    print("--------------------------------")

    rate = state.get("analysis", {}).get("budget_amount") or state.get(
        "last_offered_price"
    )

    if rate is None:
        state["final_reply"] = (
            "Could you please confirm your rate for this collaboration?"
        )
        state["next_action"] = NextAction.ASK_RATE
        print(
            f"{Colors.RED}[confirm_details_node] Missing rate, asking influencer to provide."
        )
    else:
        state["final_reply"] = (
            f"Thanks for sharing your rate of ${rate:.2f}. "
            "Could you please confirm the deliverables and timeline for this collaboration?"
        )
        state["next_action"] = NextAction.CONFIRM_DELIVERABLES

    print(f"{Colors.CYAN}Final reply prepared: {state['final_reply']}")
    print(f"{Colors.YELLOW}Exiting from confirm_details_node")
    print("--------------------------------")

    return state
