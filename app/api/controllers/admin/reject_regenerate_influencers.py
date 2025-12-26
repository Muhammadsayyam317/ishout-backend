from fastapi import HTTPException
from app.api.controllers.admin.influencers_controller import (
    find_influencers_by_campaign,
)
from app.Schemas.reject_influencer import SearchRejectRegenerateInfluencersRequest
from langfuse import observe
from app.Schemas.influencers import (
    FindInfluencerRequest,
    MoreInfluencerRequest,
)
from app.db.connection import get_db
from bson import ObjectId

from app.tools.regenerate_instagram_influencers import (
    regenerate_instagram_influencer,
)
from app.tools.regenerate_tiktok_influencers import (
    regenerate_tiktok_influencer,
)
from app.tools.regenerate_youtube_influencers import (
    regenerate_youtube_influencer,
)


@observe(name="reject_and_regenerate_influencers")
async def reject_and_regenerate_influencers(
    request_data: SearchRejectRegenerateInfluencersRequest,
):
    try:
        platform = request_data.platform.lower()
        if platform == "instagram":
            influencer = await regenerate_instagram_influencer(request_data)
        elif platform == "tiktok":
            influencer = await regenerate_tiktok_influencer(request_data)
        elif platform == "youtube":
            influencer = await regenerate_youtube_influencer(request_data)
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        return influencer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def more_influencers(request_data: MoreInfluencerRequest):
    """Simplified wrapper for fetching more influencers based on campaign"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )
        if not campaign:
            return {"error": "Campaign not found"}
        find_request = await find_influencers_by_campaign(
            request_data=FindInfluencerRequest(
                campaign_id=request_data.campaign_id,
                user_id=request_data.user_id,
                limit=request_data.more,
            )
        )
        return find_request

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in more_influencers: {str(e)}"
        ) from e
