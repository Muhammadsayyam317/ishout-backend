from app.agents.WhatsappNegotiation.graph.whatsappnegotiation_graph import (
    negotiation_graph,
)
from app.utils.printcolors import Colors


async def Negotiation_invoke(state: dict, app, config: dict | None = None):
    print(
        f"{Colors.GREEN}Entering Negotiation_invoke for thread {state.get('thread_id')}"
    )
    try:
        checkpointer = getattr(
            app.state.whatsapp_negotiation_agent, "checkpointer", None
        )
        if not checkpointer:
            raise RuntimeError("Negotiation agent Redis not initialized")

        final_state = await negotiation_graph.ainvoke(
            state,
            checkpointer=checkpointer,
            config=config,
        )
        return final_state
    finally:
        print(
            f"{Colors.GREEN}Exiting Negotiation_invoke for thread {state.get('thread_id')}"
        )
