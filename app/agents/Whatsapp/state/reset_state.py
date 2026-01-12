from app.agents.Whatsapp.state.create_user_state import create_new_state


async def reset_user_state(sender_id):
    return await create_new_state(sender_id)
