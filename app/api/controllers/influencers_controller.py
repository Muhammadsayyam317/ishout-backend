from typing import Dict, Any
import math
from app.services.agent_planner_service import plan_limits
from app.services.rag_service import retrieve_with_rag_then_fallback
from app.services.response_ranker_service import sort_and_diversify
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.services.guardrails_service import check_input_guard_rail
from app.utils.prompts import FIND_INFLUENCER_PROMPT
from app.utils.helpers import parse_follower_count, parse_follower_range
from app.models.influencers_model import FindInfluencerRequest, MoreInfluencerRequest



class Agent:
    """Simple Agent class to mimic OpenAI's Agent functionality"""
    def __init__(self, name, tools, instructions, input_guardrails=None):
        self.name = name
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails or []
        


async def find_influencers(request_data: FindInfluencerRequest):
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
                            min_val, max_val, original = parse_follower_range(raw_followers)
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
                            follower_info = {"min": min_followers, "max": max_followers, "range": raw_followers}
                        elif min_followers is not None:
                            follower_info = {"min": min_followers}

                        # Append each result to list
                        all_results.append({
                            "category": category,
                            "platform": platform,
                            "country": country,
                            "followers": follower_info,
                            "limit": per_call_limit,
                            "count": len(influencers),
                            "influencers": influencers
                        })

        # Rank and diversify before applying cap
        ranked = sort_and_diversify(global_influencers, diversify_by="platform")
        flattened = ranked[:adjusted_global_limit]

        # Add brief response notes
        notes = {
            "requested": api_limit,
            "returned": len(flattened),
            "global_cap": adjusted_global_limit,
            "strategy": "RAG-first with fallback, similarity-ranked and platform-diversified",
        }

        return {"influencers": flattened, "notes": notes}

    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}


async def more_influencers(request_data: MoreInfluencerRequest):
    """Wrapper that reuses find_influencers with the 'more' count and exclusions.

    This allows a separate, explicit endpoint for 'more' requests.
    """
    payload = FindInfluencerRequest(
        platform=request_data.platform,
        category=request_data.category,
        followers=request_data.followers,
        limit=str(request_data.more),  # base limit ignored by planner, but provided for shape
        country=request_data.country,
        more=request_data.more,
        exclude_ids=request_data.exclude_ids,
    )
    return await find_influencers(payload)