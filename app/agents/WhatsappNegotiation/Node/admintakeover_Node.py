from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors


async def admin_takeover_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering admin_takeover_node")
    print("--------------------------------")

    thread_id = state.get("thread_id")

    if not thread_id:
        print(f"{Colors.RED}[admin_takeover_node] Missing thread_id")
        return state

    print(
        f"{Colors.CYAN}[admin_takeover_node] Admin takeover triggered for thread {thread_id}"
    )
    print("--------------------------------")
    print(f"{Colors.CYAN}Thread ID: {thread_id}")
    print("--------------------------------")
    state["admin_takeover"] = True
    state["human_takeover"] = True
    state["agent_paused"] = True
    state["conversation_mode"] = "NEGOTIATION"
    state["negotiation_status"] = "manual_required"
    state["next_action"] = None

    print(f"{Colors.YELLOW}Exiting from admin_takeover_node")
    print("--------------------------------")
    return state
