from typing import Dict, Any
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
        


async def find_influencers(request_data: FindInfluencerRequest):
    """
    Handler for the find-influencer endpoint supporting cross-product search
    Each platform will be searched for each combination of category, followers, and country
    """
    try:
        all_results = []  # Collect all responses

        # Extract arrays from request
        platforms = request_data.platform
        categories = request_data.category
        followers_list = request_data.followers
        countries = request_data.country
        limit = request_data.limit

        # Validate required fields
        if not platforms or not categories:
            return {"error": "Platform and category are required"}

        # Determine API limit
        try:
            api_limit = int(limit)
        except ValueError:
            api_limit = 5

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

                        # Make API call
                        print(f"Searching {platform} for {category} influencers" + (f" in {country}" if country else "") + f" with {raw_followers} followers...")
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

                        # Append each result to list
                        all_results.append({
                            "category": category,
                            "platform": platform,
                            "country": country,
                            "followers": follower_info,
                            "limit": api_limit,
                            "count": len(influencers),
                            "influencers": influencers
                        })

        # Return all results together
        return {"results": all_results}

    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}