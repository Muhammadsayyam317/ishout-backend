from app.utils.printcolors import Colors
from app.Schemas.instagram.negotiation_schema import NextAction


def accept_negotiation_node(state):
    print(f"{Colors.GREEN}Entering into accept_negotiation_node")
    print("--------------------------------")
    state["negotiation_status"] = "agreed"
    state["final_reply"] = (
        "Great! We’re happy to proceed at this rate. We'll share next steps shortly."
    )
    state["next_action"] = NextAction.CLOSE_CONVERSATION
    print(f"{Colors.YELLOW} Exiting from accept_negotiation_node")
    print("--------------------------------")
    return state
