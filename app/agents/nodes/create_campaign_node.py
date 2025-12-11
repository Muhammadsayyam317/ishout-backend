from app.models.whatsappconversation_model import ConversationState
from app.services.whatsapp.create_whatsappcampaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")
    result = await create_whatsapp_campaign(state)
    state["campaign_id"] = result["campaign_id"]
    state["campaign_created"] = True
    state["reply"] = None
    print(f"➡ Exited node_create_campaign: {state}")
    return state
