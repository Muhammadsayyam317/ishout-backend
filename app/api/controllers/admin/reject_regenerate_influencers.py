from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from app.models.campaign_model import RejectInfluencersRequest
from app.tools.instagram_influencers import search_instagram_influencers


async def reject_and_regenerate(request: RejectInfluencersRequest):

    try:
        db = get_db()
        campaigns = db["campaigns"]
        await campaigns.update_one(
            {"_id": ObjectId(request.campaign_id)},
            {"$addToSet": {"rejected_influencers": request.rejected_influencer_id}},
        )

        campaign = await campaigns.find_one({"_id": ObjectId(request.campaign_id)})
        skip_ids = set(
            campaign["generated_influencers"] + campaign["rejected_influencers"]
        )

        new_results = await search_instagram_influencers(
            category=request.category,
            limit=1,
            followers=request.followers,
            country=request.country,
            skip_ids=skip_ids,
        )

        if new_results:
            new_id = new_results[0]["id"]
            await campaigns.update_one(
                {"_id": ObjectId(request.campaign_id)},
                {"$addToSet": {"generated_influencers": new_id}},
            )

        return {"new_influencer": new_results[0] if new_results else None}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in reject_and_regenerate: {str(e)}"
        ) from e
