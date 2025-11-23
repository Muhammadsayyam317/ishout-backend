from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from app.models.campaign_influencers_model import (
    CampaignInfluencerStatus,
    CampaignInfluencersRequest,
)
from app.utils.helpers import convert_objectid


async def companyApprovedCampaignById(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
):
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        cursor = collection.find(
            {
                "company_user_id": user_id,
                "company_approved": False,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        )
        influencers = await cursor.to_list(length=None)
        influencers = [convert_objectid(doc) for doc in influencers]
        total = await collection.count_documents(
            {
                "company_user_id": user_id,
                "company_approved": False,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        )
        total_pages = (total + page_size - 1) // page_size
        return {
            "influencers": influencers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def InfluencerApprovedByCompany(
    request_data: CampaignInfluencersRequest,
):
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        existing = await collection.find_one(
            {
                "campaign_id": ObjectId(request_data.campaign_id),
                "influencer_id": ObjectId(request_data.influencer_id),
                "platform": request_data.platform,
            }
        )
        update_fields = {
            "status": request_data.status.value,
            "company_approved": True,
        }
        if existing:
            await collection.update_one(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                },
                {"$set": update_fields},
            )
        else:
            update_fields.update(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                    "admin_approved": False,
                }
            )
            await collection.insert_one(update_fields)

        return {"message": "Influencer status update successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error approving influencer: {str(e)}"
        )
