from app.db.connection import get_db
from bson import ObjectId
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from fastapi import HTTPException

from app.models.campaign_influencers_model import CampaignInfluencerStatus


async def send_whatsapp_approved_influencers(campaign_id: str):
    db = get_db()

    campaigns_collection = db.get_collection("campaigns")
    influencer_collection = db.get_collection("campaign_influencers")
    campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})

    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

    user_phone = campaign["user_id"]
    influencers = await influencer_collection.find(
        {
            "campaign_id": ObjectId(campaign_id),
            "status": CampaignInfluencerStatus.APPROVED.value,
        }
    ).to_list(length=100)

    if not influencers:
        raise HTTPException(status_code=404, detail="No approved influencers found.")

    message = "Your approved influencers are ready! 🎉\n\n"
    for idx, inf in enumerate(influencers, start=1):
        message += (
            f"{idx}.@{inf.get('username')}\n"
            f"Picture: {inf.get('picture')}\n"
            f"Followers: {inf.get('followers')}\n"
            f"Country: {inf.get('country')}\n"
            f"Link: https://www.instagram.com/{inf.get('username')}\n"
        )

    return message
