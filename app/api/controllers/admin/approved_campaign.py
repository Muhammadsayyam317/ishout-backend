from bson import ObjectId
from fastapi import Depends, HTTPException

from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access
from app.models.campaign_influencers_model import (
    CampaignInfluencerStatus,
    CampaignInfluencersRequest,
)
from app.models.campaign_model import CampaignStatus
from app.utils.helpers import convert_objectid


async def approved_campaign(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")

        status_value = CampaignStatus.APPROVED
        query = {"status": status_value}

        projection = {
            "name": 1,
            "platform": 1,
            "category": 1,
            "followers": 1,
            "country": 1,
            "influencer_ids": 1,
            "rejected_ids": 1,
            "rejectedByUser": 1,
            "generated_influencers": 1,
            "user_id": 1,
            "status": 1,
            "limit": 1,
            "created_at": 1,
            "updated_at": 1,
        }

        total = await campaigns_collection.count_documents(query)
        cursor = (
            campaigns_collection.find(query, projection)
            .sort("created_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=None)

        formatted = []
        for doc in docs:
            influencer_ids = doc.get("influencer_ids", []) or []
            rejected_ids = doc.get("rejected_ids", []) or []
            rejected_by_user = doc.get("rejectedByUser", []) or []
            generated = doc.get("generated_influencers", []) or []

            formatted.append(
                {
                    "campaign_id": str(doc.get("_id")),
                    "name": doc.get("name"),
                    "platform": doc.get("platform"),
                    "category": doc.get("category"),
                    "followers": doc.get("followers"),
                    "country": doc.get("country"),
                    "user_id": str(doc.get("user_id")) if doc.get("user_id") else None,
                    "status": doc.get("status"),
                    "limit": doc.get("limit"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                    "total_approved": len(influencer_ids),
                    "total_rejected": len(rejected_ids),
                    "total_rejected_by_user": len(rejected_by_user),
                    "total_generated": len(generated),
                }
            )

        total_pages = total + page_size - 1

        return {
            "campaigns": formatted,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in approved campaign: {str(e)}"
        ) from e


async def approvedAdminCampaignById(
    campaign_id: str,
    current_user: dict = Depends(require_admin_access),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaign_influencers")
        cursor = campaigns_collection.find(
            {
                "campaign_id": ObjectId(campaign_id),
                "status": CampaignInfluencerStatus.APPROVED.value,
                "admin_approved": True,
                "company_approved": False,
            }
        )

        influencers = await cursor.to_list(length=None)
        cleaned = [convert_objectid(i) for i in influencers]

        return {
            "approved_influencers": cleaned,
            "total": len(cleaned),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


async def companyApprovedSingleInfluencer(
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
            "username": request_data.username,
            "picture": request_data.picture,
            "engagementRate": request_data.engagementRate,
            "bio": request_data.bio,
            "followers": request_data.followers,
            "country": request_data.country,
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

        return {"message": "Influencer approved successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error approving influencer: {str(e)}"
        )
