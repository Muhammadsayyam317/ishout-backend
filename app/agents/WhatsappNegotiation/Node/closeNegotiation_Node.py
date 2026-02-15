from app.utils.printcolors import Colors


def close_conversation_node(state):
    print(f"{Colors.GREEN}Entering into close_conversation_node")
    print("--------------------------------")
    state["negotiation_status"] = "closed"
    state["final_reply"] = "Thank you! Looking forward to working together."
    print(f"{Colors.YELLOW} Exiting from close_conversation_node")
    print("--------------------------------")
    return state
