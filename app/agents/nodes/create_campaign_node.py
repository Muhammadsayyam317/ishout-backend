from app.models.whatsappconversation_model import ConversationState
from app.services.whatsapp.create_whatsappcampaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    try:
        result = await create_whatsapp_campaign(state)
        if not result.get("success"):
            state["reply"] = (
                "Sorry, your campaign could not be created.\n\n"
                "Please try again or contact support."
            )
            state["reply_sent"] = False
            state["done"] = True
            return state

        state["campaign_id"] = result["campaign_id"]
        state["campaign_created"] = True
        state["reply"] = None

        return state

    except Exception:
        state["reply"] = (
            "Something went wrong while creating your campaign.\n\n"
            "Please try again later."
        )
        state["reply_sent"] = False
        state["done"] = True
        return state
