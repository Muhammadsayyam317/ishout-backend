from fastapi import HTTPException
from app.api.controllers.admin.reject_regenerate_influencers import (
    reject_and_regenerate_influencers,
)
from app.Schemas.reject_influencer import SearchRejectRegenerateInfluencersRequest


async def reject_and_regenerate(request_data: SearchRejectRegenerateInfluencersRequest):
    try:
        return await reject_and_regenerate_influencers(
            request_data=SearchRejectRegenerateInfluencersRequest(
                campaign_id=request_data.campaign_id,
                platform=request_data.platform,
                category=request_data.category,
                followers=request_data.followers,
                country=request_data.country,
                limit=1,
                generated_influencers_id=request_data.generated_influencers_id,
                rejected_influencers_id=request_data.rejected_influencers_id,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
