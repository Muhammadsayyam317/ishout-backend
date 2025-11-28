from fastapi import Depends, HTTPException

from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access
from app.models.campaign_influencers_model import CampaignInfluencerStatus
from app.utils.helpers import convert_objectid


async def onboarding_influencers(
    current_user: dict = Depends(require_admin_access),
):
    try:
        db = get_db()
        campaign_influencers_collection = db.get_collection("campaign_influencers")
        campaigns_collection = db.get_collection("campaigns")

        # Get distinct campaign_ids from approved influencers
        cursor = campaign_influencers_collection.find(
            {
                "admin_approved": True,
                "company_approved": True,
                "status": CampaignInfluencerStatus.APPROVED.value,
            },
            {"campaign_id": 1},
        )

        influencers = await cursor.to_list(length=None)

        # Extract unique campaign_ids
        campaign_ids = list(
            set(
                [
                    inf.get("campaign_id")
                    for inf in influencers
                    if inf.get("campaign_id")
                ]
            )
        )

        if not campaign_ids:
            return {"campaigns": [], "total": 0}

        # Query campaigns collection with those campaign_ids
        campaigns_cursor = campaigns_collection.find({"_id": {"$in": campaign_ids}})

        campaigns = await campaigns_cursor.to_list(length=None)

        # Convert ObjectIds to strings
        campaigns = [convert_objectid(campaign) for campaign in campaigns]

        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
