from app.agents.Whatsapp.nodes.state import get_conversation_round
from app.agents.Whatsapp.state.get_user_state import get_user_state
from app.agents.Whatsapp.state.update_user_state import update_user_state


async def run_whatsapp_agent(
    thread_id: str,
    msg_text: str,
    profile_name: str,
    raw_event: dict,
    app,
):

    whatsapp_agent = app.state.whatsapp_agent
    state = await get_user_state(thread_id) or {}
    round_no = await get_conversation_round(thread_id) or 1
    checkpoint_id = f"{thread_id}-r{round_no}"

    state.update(
        {
            "user_message": msg_text,
            "thread_id": thread_id,
            "sender_id": thread_id,
            "event_data": raw_event,
            "name": profile_name,
        }
    )

    final_state = await whatsapp_agent.ainvoke(
        state,
        config={"configurable": {"thread_id": checkpoint_id}},
    )
    if final_state:
        await update_user_state(thread_id, final_state)
