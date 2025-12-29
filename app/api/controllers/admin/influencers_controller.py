import asyncio
from fastapi import HTTPException
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from langfuse import observe
from app.Schemas.influencers import (
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
        exclude_ids = request_data.exclude_ids or []

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
                    exclude_ids=exclude_ids if exclude_ids else None,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_results = []
        for result in results:
            if isinstance(result, Exception):
                continue
            combined_results.extend(result.get("data", []))

        return combined_results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in find_influencers_by_campaign: {str(e)}"
        ) from e


@observe(name="more_influencers")
async def more_influencers(request_data: MoreInfluencerRequest):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        generated_collection = db.get_collection("generated_influencers")

        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        exclude_ids = await generated_collection.distinct(
            "influencer_id",
            {"campaign_id": ObjectId(request_data.campaign_id)},
        )

        request = FindInfluencerRequest(
            campaign_id=request_data.campaign_id,
            limit=request_data.limit,
            exclude_ids=exclude_ids,
        )

        result = await find_influencers_by_campaign(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in more_influencers: {str(e)}"
        ) from e
