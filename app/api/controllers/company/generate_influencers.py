from fastapi import HTTPException
from app.models.influencers_model import GenerateInfluencersRequest
from app.tools.search_influencers import search_influencers


async def generate_influencers(request_data: GenerateInfluencersRequest):
    try:
        result = await search_influencers(
            platforms=request_data.platform,
            category=request_data.category,
            followers=request_data.followers,
            country=request_data.country,
            limit=request_data.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in generate_influencers: {str(e)}"
        ) from e
