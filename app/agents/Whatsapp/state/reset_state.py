from app.agents.Whatsapp.state.create_user_state import create_new_state


async def reset_user_state(sender_id):
    print("Entering into reset_user_state")
    print("--------------------------------")
    print("Sender ID: ", sender_id)
    print("--------------------------------")
    return await create_new_state(sender_id)
