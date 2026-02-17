from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
)
from app.utils.printcolors import Colors


async def route_agent(thread_id: str):
    print(f"{Colors.CYAN}Entering Agent Router")
    print("--------------------------------")

    negotiation_state = await get_negotiation_state(thread_id)

    if negotiation_state and not negotiation_state.get("agent_paused"):
        print(f"{Colors.GREEN}Agent Router → Negotiation Agent")
        print("--------------------------------")
        return "NEGOTIATION", negotiation_state

    print(f"{Colors.YELLOW}Agent Router → Default Agent")
    print("--------------------------------")
    return "DEFAULT", None
