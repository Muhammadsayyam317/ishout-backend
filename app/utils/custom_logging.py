import time
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.model.whatsappconversation import ConversationState
import json
import logging
from typing import Coroutine
from app.utils.printcolors import Colors

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def node_debug_before(state: ConversationState):
    logging.info(
        "\n\n===== 🟡 DEBUG BEFORE =====\n%s",
        json.dumps(state, indent=2, default=str),
    )
    return state


async def node_debug_after(state: ConversationState):
    logging.info(
        "\n\n===== 🟢 DEBUG AFTER =====\n%s",
        json.dumps(state, indent=2, default=str),
    )
    return state


async def insta_debug_before(state: InstagramConversationState):
    logging.info(
        "\n\n===== 🟡 DEBUG BEFORE =====\n%s", json.dumps(state, indent=2, default=str)
    )
    return state


async def insta_debug_after(state: InstagramConversationState):
    logging.info(
        "\n\n===== 🟢 DEBUG AFTER =====\n%s", json.dumps(state, indent=2, default=str)
    )
    return state


async def whatsapp_negotiation_debug_before(state):
    print(f"{Colors.MAGENTA}========== NEGOTIATION DEBUG (BEFORE) ==========")
    print(f"Thread ID: {state.get('thread_id')}")
    print(f"User Message: {state.get('user_message')}")
    print(f"Intent: {state.get('intent')}")
    print(f"User Offer: {state.get('user_offer')}")
    print(f"Last Offered Price: {state.get('last_offered_price')}")
    print(f"Min Price: {state.get('min_price')}")
    print(f"Max Price: {state.get('max_price')}")
    print(f"Negotiation Status: {state.get('negotiation_status')}")
    print(f"Next Action: {state.get('next_action')}")
    print("===============================================")
    return state


async def whatsapp_negotiation_debug_after(state):
    print(f"{Colors.BLUE}========== NEGOTIATION DEBUG (AFTER) ==========")
    print(f"Intent: {state.get('intent')}")
    print(f"Negotiation Status: {state.get('negotiation_status')}")
    print(f"Last Offered Price: {state.get('last_offered_price')}")
    print(f"Next Action: {state.get('next_action')}")
    print(f"Manual Negotiation: {state.get('manual_negotiation')}")
    print(f"Final Reply: {state.get('final_reply')}")
    print("===============================================")
    return state


async def Background_task_logger(task_name: str, func: Coroutine, *args, **kwargs):
    start_time = time.time()
    logger.info(f"Task '{task_name}' started at {start_time}")
    try:
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Task '{task_name}' completed in {duration:.2f} seconds")
        return result
    except Exception as e:
        logger.error(f"Task '{task_name}' failed with error: {e}")
        raise e
