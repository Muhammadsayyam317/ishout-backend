from app.utils.printcolors import Colors


def reject_negotiation_node(state):
    print(f"{Colors.GREEN}Entering into reject_negotiation_node")
    print("--------------------------------")
    state["negotiation_status"] = "rejected"
    state["final_reply"] = (
        "Thanks for your time. We'll keep you in mind for future collaborations."
    )
    print(f"{Colors.YELLOW} Exiting from reject_negotiation_node")
    print("--------------------------------")
    return state
