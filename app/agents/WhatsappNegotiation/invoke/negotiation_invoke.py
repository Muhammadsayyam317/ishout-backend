from fastapi import HTTPException
from app.Schemas.whatsapp.negotiation_schema import (
    WhatsappNegotiationInitialMessageRequest,
)
from app.agents.WhatsappNegotiation.graph.whatsappnegotiation_graph import (
    whatsapp_negotiation_graph,
)
from app.agents.WhatsappNegotiation.state.negotiation_state import get_negotiation_state


async def Negotiation_invoke(request: WhatsappNegotiationInitialMessageRequest):
    print("Entering Negotiation_invoke")
    negotiation_state = await get_negotiation_state(request.thread_id)
    if negotiation_state.get("conversation_mode") != "NEGOTIATION":
        raise HTTPException(
            status_code=400,
            detail="Negotiation agent invoked for non-negotiation thread",
        )

    return await whatsapp_negotiation_graph.ainvoke(negotiation_state)
