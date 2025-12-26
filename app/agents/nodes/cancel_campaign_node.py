from app.agents.state.reset_state import reset_user_state
from app.models.whatsappconversation_model import ConversationState


async def Cancel_Campaign(state: ConversationState):
    reset_campaign = await reset_user_state()
