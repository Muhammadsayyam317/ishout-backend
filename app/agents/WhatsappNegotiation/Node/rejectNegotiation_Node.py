from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


def reject_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering reject_negotiation_node")
    print("--------------------------------")

    state["negotiation_status"] = "rejected"
    state["final_reply"] = (
        "Thanks for your time! We understand this isn’t a fit at the moment. "
        "We’ll keep you in mind for future campaigns."
    )
    state["next_action"] = None

    print(f"{Colors.CYAN}[reject_negotiation_node] Negotiation rejected")
    print(f"{Colors.YELLOW}Exiting reject_negotiation_node")
    print("--------------------------------")

    return state
