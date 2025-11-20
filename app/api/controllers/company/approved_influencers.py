from fastapi import HTTPException
from app.db.connection import get_db
from app.models.campaign_model import CampaignStatus
from app.utils.helpers import convert_objectid


async def companyApprovedCampaignById(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
):
    try:
        db = get_db()

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
            # Filter by user_id + approved influencer status
            {
                "$match": {
                    "campaign.user_id": user_id,
                    "admin_approved": True,
                    "company_approved": False,
                    "status": CampaignStatus.APPROVED.value,
                }
            },
            {"$sort": {"updated_at": -1}},
            {"$skip": skip},
            {"$limit": page_size},
        ]

        influencers = await db.campaign_influencers.aggregate(pipeline).to_list(
            length=page_size
        )
        influencers = [convert_objectid(doc) for doc in influencers]

        # Count total items for pagination
        count_pipeline = pipeline[:-3] + [{"$count": "total"}]
        total_result = await db.campaign_influencers.aggregate(count_pipeline).to_list(
            length=1
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
            "data": influencers,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
