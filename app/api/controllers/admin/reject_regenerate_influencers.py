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


@observe(name="reject_and_regenerate_influencer")
async def reject_and_regenerate_influencer(
    request_data: SearchRejectRegenerateInfluencersRequest,
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        generated_collection = db.get_collection("generated_influencers")

        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        platform = campaign["platform"][0].lower()
        categories = campaign["category"]
        followers_list = campaign["followers"]
        countries = campaign["country"]

        generated_ids = await generated_collection.distinct(
            "influencer_id", {"campaign_id": ObjectId(request_data.campaign_id)}
        )
        excluded_ids = set(generated_ids + [request_data.rejected_influencer_id])
        if platform == "instagram":
            influencer = await regenerate_instagram_influencer(
                categories=categories,
                followers=followers_list,
                countries=countries,
                exclude_ids=excluded_ids,
            )
        elif platform == "tiktok":
            influencer = await regenerate_tiktok_influencer(
                request_data=SearchRejectRegenerateInfluencersRequest(
                    categories=categories,
                    followers=followers_list,
                    countries=countries,
                    exclude_ids=excluded_ids,
                )
            )
        elif platform == "youtube":
            influencer = await regenerate_youtube_influencer(
                request_data=SearchRejectRegenerateInfluencersRequest(
                    categories=categories,
                    followers=followers_list,
                    countries=countries,
                    exclude_ids=excluded_ids,
                )
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        if influencer and influencer.get("id"):
            await generated_collection.insert_one(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": influencer["id"],
                    "username": influencer["username"],
                    "platform": influencer["platform"],
                    "followers": influencer.get("followers"),
                    "engagementRate": influencer.get("engagementRate"),
                    "country": influencer.get("country"),
                    "bio": influencer.get("bio"),
                    "picture": influencer.get("picture"),
                }
            )
        return influencer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def more_influencers(request_data: MoreInfluencerRequest):
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
