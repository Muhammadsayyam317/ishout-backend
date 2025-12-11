from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.models.campaign_model import RegenerateInfluencerRequest


async def regenerate_influencer(request_data: RegenerateInfluencerRequest):
    try:
        skip_ids = set(
            request_data.generated_influencers + request_data.rejected_influencers
        )

        if request_data.platform == "instagram":
            influencers = await search_instagram_influencers(
                category=[request_data.category],
                limit=request_data.limit,
                followers=[str(request_data.followers)],
                country=[request_data.country],
                skip_ids=skip_ids,
            )

        elif request_data.platform == "tiktok":
            influencers = await search_tiktok_influencers(
                category=[request_data.category],
                limit=request_data.limit,
                followers=[str(request_data.followers)],
                country=[request_data.country],
                skip_ids=skip_ids,
            )

        elif request_data.platform == "youtube":
            influencers = await search_youtube_influencers(
                category=[request_data.category],
                limit=request_data.limit,
                followers=[str(request_data.followers)],
                country=[request_data.country],
                skip_ids=skip_ids,
            )

        return {"status": True, "new_influencers": influencers}

    except Exception as e:
        raise ValueError(f"Error searching influencers: {str(e)}")
