from app.agents.Whatsapp.nodes.state import (
    cleanup_old_checkpoints,
    get_conversation_round,
    increment_conversation_round,
)
from app.agents.Whatsapp.state.reset_state import reset_user_state


async def prepare_state(thread_id: str, state: dict):
    round_no = await get_conversation_round(thread_id) or 1

    if state.get("done") and state.get("acknowledged"):
        round_no = await increment_conversation_round(thread_id)
        await cleanup_old_checkpoints(thread_id, round_no)
        state = await reset_user_state(thread_id)

    checkpoint_id = f"{thread_id}-r{round_no}"
    return state, checkpoint_id
