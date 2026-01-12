from app.agents.Whatsapp.state.reset_state import reset_user_state
from app.model.whatsappconversation import ConversationState


async def Cancel_Campaign(state: ConversationState):
    reset_campaign = await reset_user_state()
