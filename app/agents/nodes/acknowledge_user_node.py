from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.models.whatsappconversation_model import ConversationState


async def node_acknowledge_user(state: ConversationState, config):
    print("➡ Entered node_acknowledge_user")
    sender = state.get("sender_id") or config["configurable"]["thread_id"]

    if not state.get("acknowledged"):
        Acknowledgement_message = (
            "🎉 *Campaign Created Successfully!*\n\n"
            "Here's a summary of your campaign:\n\n"
            "📱 *Platform:* " + ", ".join(state["platform"]) + "\n"
            "🎯 *Category:* " + ", ".join(state["category"]) + "\n"
            "🌍 *Location:* " + ", ".join(state["country"]) + "\n"
            "👥 *Followers:* " + ", ".join(state["followers"]) + "\n"
            "🔢 *Number of Influencers:* " + str(state["limit"]) + "\n\n"
            "✨ Perfect iShout will shortlist matching influencers.\n\n"
            "We'll notify you once we have curated the perfect influencers for you!\n\n"
            "Thank you for choosing iShout!🎉"
        )
        await send_whatsapp_message(sender, Acknowledgement_message)
        state["acknowledged"] = True

    state["done"] = True
    print("➡ Campaign acknowledged, state marked as done")
    return state
