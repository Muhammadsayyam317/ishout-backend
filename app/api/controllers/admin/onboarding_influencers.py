from fastapi import Depends
from app.core.exception import BadRequestException, InternalServerErrorException
from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access
from app.Schemas.campaign_influencers import CampaignInfluencerStatus
from app.utils.helpers import convert_objectid
from bson import ObjectId


async def onboarding_campaigns(
    current_user: dict = Depends(require_admin_access),
    page_size: int = 10,
    page: int = 1,
):
    if page < 1 or page_size < 1:
        raise BadRequestException(message="Invalid pagination parameters")

    try:
        db = get_db()
        campaign_influencers_collection = db.get_collection("campaign_influencers")
        campaigns_collection = db.get_collection("campaigns")
        users_collection = db.get_collection("users")
        briefs_collection = db.get_collection("CampaignBriefGeneration")

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

        # Preload campaign brief logos
        brief_ids = [c.get("brief_id") for c in campaigns if c.get("brief_id")]
        brief_logo_map = {}
        if brief_ids:
            briefs = await briefs_collection.find(
                {"_id": {"$in": [str(bid) for bid in brief_ids]}}
            ).to_list(length=None)
            brief_logo_map = {
                str(doc["_id"]): (doc.get("response") or {}).get("campaign_logo_url")
                for doc in briefs
            }

        for campaign in campaigns:
            brief_id = campaign.get("brief_id")
            campaign["campaign_logo_url"] = (
                brief_logo_map.get(str(brief_id)) if brief_id else None
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
        raise InternalServerErrorException(message=str(e)) from e
