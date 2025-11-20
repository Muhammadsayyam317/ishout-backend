from fastapi import HTTPException
from bson import ObjectId

from app.db.connection import get_db
from app.models.campaign_model import CampaignStatus
from app.utils.helpers import convert_objectid


async def companyApprovedCampaignById(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
):
    try:
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="Invalid pagination parameters")

        db = get_db()
        influencers_collection = db.get_collection("campaign_influencers")

        skip = (page - 1) * page_size

        pipeline = [
            {
                "$lookup": {
                    "from": "campaigns",
                    "localField": "campaign_id",
                    "foreignField": "_id",
                    "as": "campaign",
                }
            },
            {"$unwind": "$campaign"},
            {
                "$match": {
                    "campaign.user_id": ObjectId(user_id),
                    "admin_approved": True,
                    "company_approved": False,
                    "status": CampaignStatus.APPROVED.value,
                }
            },
            {"$sort": {"updated_at": -1}},
            {"$skip": skip},
            {"$limit": page_size},
        ]

        results = await influencers_collection.aggregate(pipeline).to_list(length=None)
        results = [convert_objectid(doc) for doc in results]

        # Count total matching documents (without pagination)
        count_pipeline = [
            {
                "$lookup": {
                    "from": "campaigns",
                    "localField": "campaign_id",
                    "foreignField": "_id",
                    "as": "campaign",
                }
            },
            {"$unwind": "$campaign"},
            {
                "$match": {
                    "campaign.user_id": ObjectId(user_id),
                    "admin_approved": True,
                    "company_approved": False,
                    "status": CampaignStatus.APPROVED.value,
                }
            },
            {"$count": "total"},
        ]

        total_result = await influencers_collection.aggregate(count_pipeline).to_list(
            length=None
        )
        total = total_result[0]["total"] if total_result else 0
        total_pages = (total + page_size - 1) // page_size

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "data": results,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
