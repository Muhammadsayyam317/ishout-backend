from app.db.connection import get_db
from bson import ObjectId
from fastapi import HTTPException
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message


async def send_whatsapp_approved_influencers(campaign_id: str):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        influencer_collection = db.get_collection("campaign_influencers")

        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(
                status_code=404, detail=f"Campaign not found: {campaign_id}"
            )

        user_phone = campaign.get("user_id")
        influencers = await influencer_collection.find(
            {
                "campaign_id": ObjectId(campaign_id),
                "status": "approved",
            }
        ).to_list(length=100)

        if not influencers:
            return

        message = "🎉 Your approved influencers are ready! \n\n"
        for idx, inf in enumerate(influencers, start=1):
            message += (
                f"{idx}. @{inf.get('username')}\n"
                f"Followers: {inf.get('followers')}\n"
                f"Country: {inf.get('country')}\n"
                f"Pricing: {inf.get('pricing')}\n"
                f"Link: https://www.instagram.com/{inf.get('username')}\n\n"
            )
        success = await send_whatsapp_message(user_phone, message)
        if not success:
            raise HTTPException(
                status_code=500, detail="WhatsApp message failed to send."
            )
        return {"message": "WhatsApp message sent successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in send_whatsapp_approved_influencers: {str(e)}",
        ) from e
