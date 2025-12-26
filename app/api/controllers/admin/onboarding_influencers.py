from fastapi import Depends, HTTPException
from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access
from app.Schemas.campaign_influencers import CampaignInfluencerStatus
from app.utils.helpers import convert_objectid


async def onboarding_campaigns(
    current_user: dict = Depends(require_admin_access),
    page_size: int = 10,
    page: int = 1,
):
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")

    try:
        db = get_db()
        campaign_influencers_collection = db.get_collection("campaign_influencers")
        campaigns_collection = db.get_collection("campaigns")
        cursor = campaign_influencers_collection.find(
            {
                "admin_approved": True,
                "company_approved": True,
                "status": CampaignInfluencerStatus.APPROVED.value,
            },
            {"campaign_id": 1},
        )
        influencers = await cursor.to_list(length=None)

        campaign_counts = {}
        campaign_ids = []
        for influencer in influencers:
            campaign_id = influencer.get("campaign_id")
            if not campaign_id:
                continue
            campaign_counts[campaign_id] = campaign_counts.get(campaign_id, 0) + 1
            if campaign_id not in campaign_ids:
                campaign_ids.append(campaign_id)

        if not campaign_ids:
            return {
                "campaigns": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False,
            }
        total = await campaigns_collection.count_documents(
            {"_id": {"$in": campaign_ids}}
        )
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        campaigns_cursor = (
            campaigns_collection.find({"_id": {"$in": campaign_ids}})
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        campaigns = await campaigns_cursor.to_list(length=page_size)

        for campaign in campaigns:
            campaign["approved_influencer_count"] = campaign_counts.get(
                campaign.get("_id"), 0
            )

        campaigns = [convert_objectid(campaign) for campaign in campaigns]

        return {
            "campaigns": campaigns,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
