from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.agents.WhatsappNegotiation.Node.send_reply_Node import send_whatsapp_reply_node
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    update_negotiation_state,
)
from app.utils.printcolors import Colors
from app.core.exception import InternalServerErrorException


async def complete_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering complete_negotiation_node")
    print("--------------------------------")
    try:
        campaign_id = state.get("campaign_id")
        await update_negotiation_state(
            thread_id=state["thread_id"],
            data={
                "conversation_mode": "DEFAULT",
                "human_takeover": False,
                "campaign_id": campaign_id,
                "negotiation_completed": True,
                "negotiation_status": "agreed",
            },
        )
        print(
            f"{Colors.CYAN}[complete_negotiation_node] Negotiation state updated successfully"
        )
        print("--------------------------------")

        message_text = (
            "Thanks for sharing the details 🙌\n\n"
            "Our collaboration team will now discuss pricing and next steps with you."
        )
        state["final_reply"] = message_text
        await send_whatsapp_reply_node(state)
        state["final_reply"] = message_text
        state["next_action"] = None

        print(f"{Colors.YELLOW}Exiting from complete_negotiation_node")
        print("--------------------------------")

    except Exception as e:
        print(f"{Colors.RED}[complete_negotiation_node] Error: {e}")
        raise InternalServerErrorException(
            message=f"Error in complete_negotiation_node: {str(e)}"
        ) from e

    return state
