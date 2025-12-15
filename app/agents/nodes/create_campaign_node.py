from app.models.whatsappconversation_model import ConversationState
from app.services.whatsapp.create_whatsappcampaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")

    try:
        result = await create_whatsapp_campaign(state)

        if result.get("success"):
            state["campaign_id"] = result.get("campaign_id")
            state["campaign_created"] = True
            state["ready_for_campaign"] = False
        else:
            state["reply"] = (
                "❌ Sorry, something went wrong while creating your campaign.\n\n"
                "Please try again later or contact support."
            )
            state["reply_sent"] = False
            state["ready_for_campaign"] = False
            state["done"] = True

    except Exception as e:
        print(f"❌ Error in node_create_campaign: {e}")
        state["reply"] = (
            "❌ Sorry, something went wrong while creating your campaign.\n\n"
            "Please try again later or contact support."
        )
        state["reply_sent"] = False
        state["ready_for_campaign"] = False
        state["done"] = True

    return state
