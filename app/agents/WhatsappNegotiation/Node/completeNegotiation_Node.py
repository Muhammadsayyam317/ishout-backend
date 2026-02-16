from app.agents.WhatsappNegotiation.state.negotiation_state import (
    update_negotiation_state,
)
from app.services.whatsapp.send_text import send_message_from_ishout_to_user
from app.utils.Enums.user_enum import SenderType
from app.utils.printcolors import Colors
from app.core.exception import InternalServerErrorException


async def complete_negotiation_node(state):
    try:
        print(f"{Colors.GREEN}Entering into complete_negotiation_node")
        print("--------------------------------")
        await update_negotiation_state(
            thread_id=state["thread_id"],
            data={
                "conversation_mode": "DEFAULT",
                "human_takeover": False,
                "campaign_id": state["campaign_id"],
                "negotiation_completed": True,
            },
        )
        print(f"{Colors.CYAN} [complete_negotiation_node] Negotiation state updated")
        print("--------------------------------")

        await send_message_from_ishout_to_user(
            user_id=state["thread_id"],
            text=(
                "Thanks for sharing the details 🙌\n\n"
                "Our collaboration team will now discuss pricing and next steps with you."
            ),
            sender=SenderType.AI.value,
        )
        print(f"{Colors.YELLOW} Exiting from complete_negotiation_node")
        print("--------------------------------")
    except Exception as e:
        print(f"{Colors.RED}Error in complete_negotiation_node: {e}")
        print("--------------------------------")
        raise InternalServerErrorException(
            message=f"Error in complete_negotiation_node: {str(e)}"
        ) from e
    return state
