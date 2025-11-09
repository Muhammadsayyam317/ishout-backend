from typing import Dict, Any
from fastapi import HTTPException
from app.services.agent_planner_service import plan_limits
from app.services.rag_service import retrieve_with_rag_then_fallback
from app.services.response_ranker_service import sort_and_diversify
from app.services.campaign_service import create_campaign, add_rejected_influencers
from app.models.campaign_model import CreateCampaignRequest
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.utils.helpers import parse_follower_count, parse_follower_range
from app.models.influencers_model import (
    FindInfluencerRequest,
    MoreInfluencerRequest,
    FindInfluencerLegacyRequest,
    MoreInfluencerLegacyRequest,
)
from app.db.connection import get_db
from bson import ObjectId


class Agent:
    """Simple Agent class to mimic OpenAI's Agent functionality"""


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

        for platform in platforms:
            platform = platform.strip().lower()

            # Choose platform tool
            if platform == "instagram":
                tool = search_instagram_influencers
            elif platform == "tiktok":
                tool = search_tiktok_influencers
            elif platform == "youtube":
                tool = search_youtube_influencers
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported platform: {platform}"
                )

        result = await tool(
            category=categories,
            limit=limit,
            followers=followers_list,
            country=countries,
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in find_influencers_by_campaign: {str(e)}"
        ) from e


async def find_influencers(request_data: FindInfluencerLegacyRequest):
    """
    Handler for the find-influencer endpoint supporting cross-product search
    Each platform will be searched for each combination of category, followers, and country
    """
    try:
        all_results = []  # Collect all responses
        global_influencers: list = []  # Flattened, deduped influencer pool
        seen_keys = set()

        # Extract arrays from request
        platforms = request_data.platform
        categories = request_data.category
        followers_list = request_data.followers
        countries = request_data.country
        limit = request_data.limit
        more = getattr(request_data, "more", None)
        exclude_ids = set(getattr(request_data, "exclude_ids", []) or [])
        is_campaign_create = request_data.is_campaign_create

        # Validate required fields
        if not platforms or not categories:
            return {"error": "Platform and category are required"}

        # Determine API limit (treat as global requested count), then adjust
        try:
            api_limit = int(limit)
        except ValueError:
            api_limit = 5

        # Agentic planning for limits (use `more` when present for follow-up requests)
        effective_limit = int(more) if more else api_limit
        adjusted_global_limit, per_call_limit = plan_limits(
            user_limit=effective_limit,
            categories=categories,
            followers_list=followers_list,
            countries=countries,
        )

        # Create cross-product search: each platform × each category × each follower count × each country
        for platform in platforms:
            platform = platform.strip().lower()

            # Choose platform tool
            if platform == "instagram":
                tool = search_instagram_influencers
            elif platform == "tiktok":
                tool = search_tiktok_influencers
            elif platform == "youtube":
                tool = search_youtube_influencers
            else:
                all_results.append({"error": f"Unsupported platform: {platform}"})
                continue

            for category in categories:
                category = category.strip()

                for raw_followers in followers_list:
                    raw_followers = raw_followers.strip()

                    # Parse followers (range or single)
                    min_followers = max_followers = None
                    if raw_followers:
                        if "-" in raw_followers:
                            min_val, max_val, original = parse_follower_range(
                                raw_followers
                            )
                            min_followers, max_followers = min_val, max_val
                        else:
                            min_followers = parse_follower_count(raw_followers)

                    for country in countries:
                        country = country.strip() if country else None

                        # Build descriptive query
                        if min_followers is not None:
                            if max_followers is not None:
                                query = f"find {category} influencers with {min_followers}-{max_followers} followers"
                            else:
                                query = f"find {category} influencers with at least {min_followers} followers"
                        else:
                            query = f"find {category} influencers"

                        influencers = await retrieve_with_rag_then_fallback(
                            platform=platform,
                            category=category,
                            country=country,
                            raw_followers=raw_followers,
                            min_followers=min_followers,
                            max_followers=max_followers,
                            per_call_limit=per_call_limit,
                            tool_call=tool,
                            query=query,
                            seen_keys=seen_keys,
                            exclude_keys=exclude_ids,
                        )

                        # collect into global pool for final flattening
                        global_influencers.extend(influencers)

                        follower_info = {}
                        if min_followers is not None and max_followers is not None:
                            follower_info = {
                                "min": min_followers,
                                "max": max_followers,
                                "range": raw_followers,
                            }
                        elif min_followers is not None:
                            follower_info = {"min": min_followers}

                        # Append each result to list
                        all_results.append(
                            {
                                "category": category,
                                "platform": platform,
                                "country": country,
                                "followers": follower_info,
                                "limit": per_call_limit,
                                "count": len(influencers),
                                "influencers": influencers,
                            }
                        )

        # Rank and diversify before applying cap
        ranked = sort_and_diversify(global_influencers, diversify_by="platform")
        flattened = ranked[:adjusted_global_limit]

        campaign_response = None

        # Auto-create campaign if campaign details provided (silent creation)
        if is_campaign_create:
            campaign_name = (
                request_data.campaign_name or f"Campaign - {', '.join(categories)}"
            )
            campaign_description = (
                request_data.campaign_description
                or f"Auto-generated campaign for {', '.join(categories)} influencers on {', '.join(platforms)}"
            )

            campaign_request = CreateCampaignRequest(
                name=campaign_name,
                description=campaign_description,
                platform=platforms,
                category=categories,
                followers=followers_list,
                country=countries,
                influencer_ids=[],
                user_id=getattr(
                    request_data, "user_id", None
                ),  # Include user_id if provided
            )

            # Create campaign and capture response
            campaign_response = await create_campaign(campaign_request)

        # Add brief response notes
        notes = {
            "requested": api_limit,
            "returned": len(flattened),
            "global_cap": adjusted_global_limit,
            "strategy": "RAG-first with fallback, similarity-ranked and platform-diversified",
        }

        response: Dict[str, Any] = {"influencers": flattened, "notes": notes}
        if campaign_response is not None:
            response["campaign"] = campaign_response
        return response

    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}


async def more_influencers(request_data: MoreInfluencerRequest):
    """Simplified wrapper for fetching more influencers based on campaign"""
    try:
        # Create a FindInfluencerRequest with the more count
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )
        if not campaign:
            return {"error": "Campaign not found"}
        find_request = await find_influencers_by_campaign(campaign)

        # Use the simplified find function
        return find_request

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in more_influencers: {str(e)}"
        ) from e


async def more_influencers_legacy(request_data: MoreInfluencerLegacyRequest):
    """Legacy wrapper that reuses find_influencers with the 'more' count and exclusions"""
    # Use exclude_ids as the set of rejected/seen influencers
    combined_exclude = list({*(request_data.exclude_ids or [])})

    # Optionally record rejections to campaign (exclude_ids are considered rejected)
    if request_data.campaign_id and request_data.exclude_ids:
        try:
            return await add_rejected_influencers(
                request_data.campaign_id, combined_exclude
            )
        except Exception:
            pass

    payload = FindInfluencerLegacyRequest(
        platform=request_data.platform,
        category=request_data.category,
        followers=request_data.followers,
        limit=str(
            request_data.more
        ),  # base limit ignored by planner, but provided for shape
        country=request_data.country,
        more=request_data.more,
        exclude_ids=combined_exclude,
        campaign_id=request_data.campaign_id,
    )
    return await find_influencers(payload)
