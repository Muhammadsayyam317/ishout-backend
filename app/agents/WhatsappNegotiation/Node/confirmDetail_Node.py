from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


def confirm_details_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into confirm_details_node")
    print("--------------------------------")
    rate = state.get("analysis", {}).get("budget_amount")

    state["final_reply"] = (
        f"Thanks for sharing your rate of ${rate:.2f}. "
        "Could you please confirm the deliverables and timeline for this collaboration?"
    )

    print(f"{Colors.CYAN} [confirm_details_node] Final reply: {state['final_reply']}")
    print(f"{Colors.YELLOW} Exiting from confirm_details_node")
    print("--------------------------------")
    return state
