from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.db.connection import get_db
from bson import ObjectId
from fastapi import HTTPException


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
            print(
                f"[send_whatsapp_approved_influencers] No influencers found for campaign {campaign_id}"
            )
            return

        for influencer in influencers:
            print(
                f"[send_whatsapp_approved_influencers] Sending message to {user_phone} with content: {influencer}"
            )
            success = await send_whatsapp_message(
                user_phone, "Approve or Reject this influencer?", influencer
            )

            if not success:
                print(f"WhatsApp message failed to send to {user_phone}")
                raise HTTPException(
                    status_code=500, detail="WhatsApp message failed to send."
                )
        return {"message": "WhatsApp message sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
