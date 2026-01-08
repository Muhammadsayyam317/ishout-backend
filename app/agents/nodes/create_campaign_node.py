from app.Schemas.whatsappconversation import ConversationState
from app.services.whatsapp.create_campaign import create_whatsapp_campaign


async def node_create_campaign(state: ConversationState):
    print("Entering node_create_campaign")
    try:
        result = await create_whatsapp_campaign(state)
        print("Result: ", result)
        if not result.get("success"):
            state["reply"] = (
                "Sorry, your campaign could not be created.\n\n"
                "Please try again or contact support.If the problem persists, please contact support."
            )
            state["reply_sent"] = False
            state["done"] = True
            return state

        state["campaign_id"] = result["campaign_id"]
        state["campaign_created"] = True
        state["reply"] = None
        print("Exiting node_create_campaign successfully")
        return state

    except Exception:
        print("❌ Error in node_create_campaign")
        state["reply"] = (
            "Something went wrong while creating your campaign.\n\n"
            "Please try again later."
        )
        state["reply_sent"] = False
        state["done"] = True
        return state
