from app.models.whatsappconversation_model import ConversationState
from app.services.whatsapp.create_whatsappcampaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")

    try:
        categories = state.get("category") or []
        platforms = state.get("platform") or []

        category_str = ", ".join(categories) if categories else "General"
        platform_str = ", ".join(platforms) if platforms else "General"

        state["category"] = categories
        state["platform"] = platforms
        state["campaign_name_safe"] = f"Campaign - {category_str} - {platform_str}"

        result = await create_whatsapp_campaign(state)

        state["campaign_id"] = result.get("campaign_id")
        state["campaign_created"] = True
        state["reply"] = None

    except Exception as e:
        print(f"❌ Error in node_create_campaign: {e}")
        state["reply"] = (
            "❌ Sorry, something went wrong while creating your campaign.\n\n"
            "Please try again later or contact support."
        )
        state["reply_sent"] = False
        state["done"] = True

    return state
