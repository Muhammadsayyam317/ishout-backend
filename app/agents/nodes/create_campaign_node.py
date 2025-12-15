from app.models.whatsappconversation_model import ConversationState
from app.services.whatsapp.create_whatsappcampaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")

    try:
        result = await create_whatsapp_campaign(state)

        # 🔴 HARD CHECK
        if not result.get("success"):
            print("❌ Campaign creation failed:", result)

            state["reply"] = (
                "❌ Sorry, your campaign could not be created.\n\n"
                "Please try again or contact support."
            )
            state["reply_sent"] = False
            state["done"] = True
            return state

        # Only here campaign is really created
        state["campaign_id"] = result["campaign_id"]
        state["campaign_created"] = True
        state["reply"] = None

        return state

    except Exception as e:
        print(f"❌ Error in node_create_campaign: {e}")

        state["reply"] = (
            "❌ Something went wrong while creating your campaign.\n\n"
            "Please try again later."
        )
        state["reply_sent"] = False
        state["done"] = True
        return state
