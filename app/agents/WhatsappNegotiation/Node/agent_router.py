from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
)


async def route_agent(thread_id: str):
    control_state = await get_negotiation_state(thread_id)

    if (
        control_state
        and control_state.get("conversation_mode") == "NEGOTIATION"
        and not control_state.get("agent_paused")
    ):
        return "NEGOTIATION"

    return "DEFAULT"
