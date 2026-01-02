from app.core.exception import InternalServerErrorException, NotFoundException
from app.db.connection import get_db
from bson import ObjectId
from app.utils.Enums.status_enum import CampaignInfluencerStatus
from app.services.whatsapp.onboarding_message import send_whatsapp_message


async def send_whatsapp_approved_influencers(campaign_id: str):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        influencer_collection = db.get_collection("campaign_influencers")

        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise NotFoundException(message=f"Campaign not found: {campaign_id}")

        user_phone = campaign.get("user_id")
        influencers = await influencer_collection.find(
            {
                "campaign_id": ObjectId(campaign_id),
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        ).to_list(length=100)
        if not influencers:
            return

        for influencer in influencers:
            success = await send_whatsapp_message(
                user_phone, "Approve or Reject this influencer?", influencer
            )

            if not success:
                raise InternalServerErrorException(
                    status_code=500, detail="WhatsApp message failed to send."
                )
        return {"message": "WhatsApp message sent successfully!"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e
