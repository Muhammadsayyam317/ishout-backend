from bson import ObjectId
from app.db.connection import get_db
from app.Schemas.campaign_influencers import CampaignInfluencerStatus
from app.services.whatsapp.send_text import send_whatsapp_text_message


async def check_and_send_campaign_summary(campaign_id: str, sender_id: str):
    try:
        print("Entering into check_and_send_campaign_summary")
        db = get_db()
        influencers_col = db.get_collection("campaign_influencers")
        campaigns_col = db.get_collection("campaigns")

        # All admin-approved influencers
        total = await influencers_col.count_documents(
            {
                "campaign_id": campaign_id,
                "admin_approved": True,
            }
        )

        # All decided by company
        decided = await influencers_col.count_documents(
            {
                "campaign_id": campaign_id,
                "admin_approved": True,
                "company_approved": True,
            }
        )

        # Not done yet
        if total == 0 or decided < total:
            return

        # Prevent sending summary twice
        campaign = await campaigns_col.find_one({"_id": campaign_id})
        if campaign.get("summary_sent"):
            return

        # Build summary
        approved = await influencers_col.count_documents(
            {
                "campaign_id": campaign_id,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        )

        rejected = await influencers_col.count_documents(
            {
                "campaign_id": campaign_id,
                "status": CampaignInfluencerStatus.REJECTED.value,
            }
        )

        summary_message = (
            "*Campaign Summary*\n\n"
            f"✅ Number of Approved Influencers: {approved}\n"
            f"❌ Number of Rejected Influencers: {rejected}\n\n"
            "🎉 Your campaign Influencer selection is complete!"
        )

        # Send WhatsApp summary
        await send_whatsapp_text_message(sender_id, summary_message)

        # Mark summary as sent
        await campaigns_col.update_one(
            {"_id": ObjectId(campaign_id)}, {"$set": {"summary_sent": True}}
        )
        print("Exiting from check_and_send_campaign_summary")
        return True
    except Exception:
        print("❌ Error in check_and_send_campaign_summary")
        return False
