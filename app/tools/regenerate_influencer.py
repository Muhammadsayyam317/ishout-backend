from fastapi import HTTPException
from app.Schemas.reject_influencer import SearchRejectRegenerateInfluencersRequest
from app.api.controllers.admin.reject_regenerate_influencers import (
    reject_and_regenerate_influencer,
)


async def reject_and_regenerate(request_data: SearchRejectRegenerateInfluencersRequest):
    try:
        return await reject_and_regenerate_influencer(
            request_data=SearchRejectRegenerateInfluencersRequest(
                campaign_id=request_data.campaign_id,
                platform=request_data.platform,
                category=request_data.category,
                followers=request_data.followers,
                country=request_data.country,
                limit=1,
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
