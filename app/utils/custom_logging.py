from app.model.whatsappconversation import ConversationState
import json
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
