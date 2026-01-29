from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.services.instagram.send_instagram_message import Send_Insta_Message
import logging

logger = logging.getLogger(__name__)


async def send_reply(state: InstagramConversationState):
    print("Entering into Node Send Reply")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    if not state.get("final_reply"):
        return state

    await Send_Insta_Message(
        message=state["final_reply"], recipient_id=state["thread_id"]
    )
    logger.debug(f"Sent reply to thread {state['thread_id']}")
    print("Exiting from Node Send Reply")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
