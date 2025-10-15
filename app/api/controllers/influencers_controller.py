from typing import Dict, Any, List
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.services.guardrails_service import check_input_guard_rail
from app.utils.prompts import FIND_INFLUENCER_PROMPT
from app.utils.helpers import parse_follower_count, parse_follower_range
from app.models.influencers_model import FindInfluencerRequest



class Agent:
    """Simple Agent class to mimic OpenAI's Agent functionality"""
    def __init__(self, name, tools, instructions, input_guardrails=None):
        self.name = name
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails or []
        


async def find_influencers(request_data: List[FindInfluencerRequest]):
    """
    Handler for the find-influencer endpoint supporting multiple payloads
    """
    try:
        all_results = []  # ✅ Step 3: Collect all responses

        for req in request_data:
            # Extract single values from request
            category = req.category.strip()
            platform = req.platform.strip()
            raw_followers = (req.followers or "").strip()
            country = (req.country or "").strip() if req.country else None
            limit = req.limit

            # Validate required fields
            if not category or not platform:
                all_results.append({"error": "Category and platform are required"})
                continue

            # Parse followers (range or single)
            min_followers = max_followers = None
            if raw_followers:
                if "-" in raw_followers:
                    min_val, max_val, original = parse_follower_range(raw_followers)
                    min_followers, max_followers = min_val, max_val
                else:
                    min_followers = parse_follower_count(raw_followers)

            # Determine API limit
            try:
                api_limit = int(limit)
            except ValueError:
                api_limit = 5

            # Build descriptive query
            if min_followers is not None:
                if max_followers is not None:
                    query = f"find {category} influencers with {min_followers}-{max_followers} followers"
                else:
                    query = f"find {category} influencers with at least {min_followers} followers"
            else:
                query = f"find {category} influencers"

            # Choose platform tool
            if platform.lower() == "instagram":
                tool = search_instagram_influencers
            elif platform.lower() == "tiktok":
                tool = search_tiktok_influencers
            elif platform.lower() == "youtube":
                tool = search_youtube_influencers
            else:
                all_results.append({"error": f"Unsupported platform: {platform}"})
                continue

            # Make API call
            print(f"Searching {platform} for {category} influencers" + (f" in {country}" if country else "") + "...")
            result = await tool(
                query=query,
                limit=api_limit,
                min_followers=min_followers,
                max_followers=max_followers,
                country=country
            )

            influencers = result.get("influencers", [])

            follower_info = {}
            if min_followers is not None and max_followers is not None:
                follower_info = {"min": min_followers, "max": max_followers, "range": raw_followers}
            elif min_followers is not None:
                follower_info = {"min": min_followers}

            # ✅ Step 4: Append each result to list
            all_results.append({
                "input": req.dict(),
                "category": category,
                "platform": platform,
                "country": country,
                "followers": follower_info,
                "limit": api_limit,
                "count": len(influencers),
                "influencers": influencers
            })

        # ✅ Step 5: Return all results together
        return {"results": all_results}

    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}