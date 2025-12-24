import asyncio
from fastapi import HTTPException
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from langfuse import observe
from app.models.influencers_model import (
    FindInfluencerRequest,
    MoreInfluencerRequest,
)
from app.db.connection import get_db
from bson import ObjectId


@observe(name="find_influencers_by_campaign")
async def find_influencers_by_campaign(request_data: FindInfluencerRequest):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        platforms = campaign["platform"]
        categories = campaign["category"]
        followers_list = campaign["followers"]
        countries = campaign["country"]
        limit = request_data.limit
        if not platforms or not categories:
            raise HTTPException(
                status_code=400,
                detail="Campaign must have platform and category specified",
            )
        tasks = []
        for platform in platforms:
            platform_normalized = platform.strip().lower()

            if platform_normalized == "instagram":
                tool = search_instagram_influencers
            elif platform_normalized == "tiktok":
                tool = search_tiktok_influencers
            elif platform_normalized == "youtube":
                tool = search_youtube_influencers
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported platform: {platform}"
                )
            tasks.append(
                tool(
                    category=categories,
                    limit=limit,
                    followers=followers_list,
                    country=countries,
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        combined_results = []
        for result in results:
            if isinstance(result, Exception):
                continue
            combined_results.extend(result)

        return combined_results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in find_influencers_by_campaign: {str(e)}"
        ) from e


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
