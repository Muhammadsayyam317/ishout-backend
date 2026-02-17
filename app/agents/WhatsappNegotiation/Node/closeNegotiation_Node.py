from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


def close_conversation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering close_conversation_node")
    print("--------------------------------")

    state["negotiation_status"] = "closed"
    state["final_reply"] = "Thank you! Looking forward to working together."
    state["next_action"] = None

    print(f"{Colors.CYAN}Conversation closed. Reply: {state['final_reply']}")
    print(f"{Colors.YELLOW}Exiting from close_conversation_node")
    print("--------------------------------")

    return state
