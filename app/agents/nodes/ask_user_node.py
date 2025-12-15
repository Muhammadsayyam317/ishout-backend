# from app.agents.state.update_user_state import update_user_state
# from app.models.whatsappconversation_model import ConversationState
# from app.services.whatsapp.onboarding_Whatsapp_message import send_whatsapp_message


# async def node_ask_user(state: ConversationState, config):
#     print(f"➡ Entered node_ask_user: {state}")
#     sender = state.get("sender_id") or config["configurable"]["thread_id"]
#     if state.get("reply") and not state.get("reply_sent"):
#         await send_whatsapp_message(sender, state["reply"])
#         state["reply_sent"] = True
#         await update_user_state(sender, state)
#     print(f"➡ Exited node_ask_user: {state}")
#     return state
