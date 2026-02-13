from app.agents.WhatsappNegotiation.graph.whatsappnegotiation_graph import (
    whatsapp_negotiation_graph,
)


async def Negotiation_invoke(state: dict, config: dict | None = None):
    print("Entering Negotiation_invoke")
    final_state = await whatsapp_negotiation_graph.ainvoke(
        state,
        config=config,
    )

    return final_state
