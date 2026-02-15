import time
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.model.whatsappconversation import ConversationState
import json
import logging
from typing import Coroutine

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

    # For Instagram


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


async def negotiation_debug_before(state: WhatsappNegotiationState):
    logging.info(
        "\n\n===== 🟡 DEBUG BEFORE =====\n%s", json.dumps(state, indent=2, default=str)
    )
    return state


async def negotiation_debug_after(state: WhatsappNegotiationState):
    logging.info(
        "\n\n===== 🟢 DEBUG AFTER =====\n%s", json.dumps(state, indent=2, default=str)
    )
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
