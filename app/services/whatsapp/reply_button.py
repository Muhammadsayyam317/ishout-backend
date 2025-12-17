from bson import ObjectId
from datetime import datetime, timezone
from app.db.connection import get_db
from app.models.campaign_influencers_model import CampaignInfluencerStatus
from app.services.whatsapp.send_text import send_whatsapp_text_message


async def handle_button_reply(message: dict):
    interactive = message.get("interactive", {})
    button_reply = interactive.get("button_reply", {})

    reply_id = button_reply.get("id")
    sender_id = message.get("from")

    if not reply_id or "_" not in reply_id:
        return

    action, influencer_doc_id = reply_id.split("_", 1)

    db = get_db()
    collection = db.get_collection("campaign_influencers")

    influencer = await collection.find_one({"_id": ObjectId(influencer_doc_id)})

    #  Prevent invalid / missing influencer
    if not influencer:
        await send_whatsapp_text_message(sender_id, "⚠ Influencer record not found.")
        return

    # PREVENT DOUBLE ACTION
    if influencer.get("company_approved") is True:
        await send_whatsapp_text_message(
            sender_id, f"⚠ You already responded for @{influencer.get('username')}."
        )
        return

    # ✅ Determine new status
    if action == "approve":
        new_status = CampaignInfluencerStatus.APPROVED.value
        confirmation_text = (
            f"✅ You APPROVED @{influencer.get('username')}.\n"
            "They have been added to your campaign."
        )
    elif action == "reject":
        new_status = CampaignInfluencerStatus.REJECTED.value
        confirmation_text = (
            f"❌ You REJECTED @{influencer.get('username')}.\n"
            "They will not be included in this campaign."
        )
    else:
        return

    # 🧠 UPDATE DB (THIS DISABLES BUTTON LOGICALLY)
    await collection.update_one(
        {"_id": influencer["_id"]},
        {
            "$set": {
                "status": new_status,
                "company_approved": True,
                "company_decision_at": datetime.now(timezone.utc),
            }
        },
    )

    # 📩 SEND CONFIRMATION MESSAGE
    await send_whatsapp_text_message(sender_id, confirmation_text)
