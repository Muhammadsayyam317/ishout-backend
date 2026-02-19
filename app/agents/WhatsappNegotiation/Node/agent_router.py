from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
)
from app.utils.printcolors import Colors


async def route_agent(thread_id: str):
    print(f"{Colors.CYAN}Entering Agent Router")
    print("--------------------------------")

    control_state = await get_negotiation_state(thread_id)

    if (
        control_state
        and control_state.get("conversation_mode") == "NEGOTIATION"
        and not control_state.get("agent_paused")
    ):
        print(f"{Colors.GREEN}Agent Router → Negotiation Agent")
        print("--------------------------------")
        return "NEGOTIATION"

    print(f"{Colors.YELLOW}Agent Router → Default Agent")
    print("--------------------------------")
    return "DEFAULT"
