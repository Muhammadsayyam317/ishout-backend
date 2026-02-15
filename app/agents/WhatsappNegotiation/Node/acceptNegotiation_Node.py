from app.utils.printcolors import Colors


def accept_negotiation_node(state):
    print(f"{Colors.GREEN}Entering into accept_negotiation_node")
    print("--------------------------------")
    state["negotiation_status"] = "agreed"
    state["final_reply"] = (
        "Great! We’re happy to proceed at this rate. We'll share next steps shortly."
    )
    print(f"{Colors.YELLOW} Exiting from accept_negotiation_node")
    print("--------------------------------")
    return state
