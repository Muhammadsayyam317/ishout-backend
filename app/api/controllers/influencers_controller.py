from typing import Dict, Any
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.services.guardrails_service import check_input_guard_rail
from app.utils.prompts import FIND_INFLUENCER_PROMPT
from app.utils.helpers import parse_follower_count, parse_follower_range



class Agent:
    """Simple Agent class to mimic OpenAI's Agent functionality"""
    def __init__(self, name, tools, instructions, input_guardrails=None):
        self.name = name
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails or []
        



async def find_influencers(request_data: Dict[str, Any]):
    """Handler for the find-influencer endpoint for single queries"""
    try:
        # Extract single values from request
        category = str(request_data.get("category", "")).strip()
        platform = str(request_data.get("platform", "")).strip()
        raw_followers = str(request_data.get("followers", "")).strip()
        limit = str(request_data.get("limit")).strip()
        
        # Validate required fields
        if not category or not platform:
            return {"error": "Category and platform are required"}
        
        # Parse followers if provided - handle both single values and ranges
        min_followers = None
        max_followers = None
        if raw_followers:
            if "-" in raw_followers:
                # It's a range like "15K-25K", use parse_follower_range to get min value
                min_val, max_val, original = parse_follower_range(raw_followers)
                min_followers = min_val
                max_followers = max_val
                print(f"Parsed follower range '{raw_followers}': min={min_val}, max={max_val}")
            else:
                # It's a single value, use parse_follower_count
                min_followers = parse_follower_count(raw_followers)
                print(f"Parsed single follower count '{raw_followers}': {min_followers}")
        
        # Parse limit to integer
        try:
            api_limit = int(limit)
        except ValueError:
            api_limit = 5
        
        # Build query with proper follower formatting
        if min_followers is not None:
            if max_followers is not None:
                # Range query - make it more descriptive
                if min_followers >= 1000000:
                    min_str = f"{min_followers//1000000}M"
                    max_str = f"{max_followers//1000000}M"
                elif min_followers >= 1000:
                    min_str = f"{min_followers//1000}K"
                    max_str = f"{max_followers//1000}K"
                else:
                    min_str = str(min_followers)
                    max_str = str(max_followers)
                query = f"find {category} influencers with {min_str} to {max_str} followers"
            else:
                # Single value query
                if min_followers >= 1000000:
                    follower_str = f"{min_followers//1000000}M"
                elif min_followers >= 1000:
                    follower_str = f"{min_followers//1000}K"
                else:
                    follower_str = str(min_followers)
                query = f"find {category} influencers with at least {follower_str} followers"
        else:
            query = f"find {category} influencers"
        
        # Select tool based on platform
        if platform.lower() == "instagram":
            tool = search_instagram_influencers
        elif platform.lower() == "tiktok":
            tool = search_tiktok_influencers
        elif platform.lower() == "youtube":
            tool = search_youtube_influencers
        else:
            return {"error": f"Unsupported platform: {platform}"}
        
        # Print the search
        print(f"Searching for {category} influencers on {platform} with min_followers: {min_followers}, max_followers: {max_followers}, limit: {api_limit}")
        
        # Make the API call with follower filters
        result = await tool(query=query, limit=api_limit, min_followers=min_followers, max_followers=max_followers)
        
        # Get the influencers from the result
        influencers = result.get("influencers", [])
        
        # Return simplified response with follower filter info
        follower_info = {}
        if min_followers is not None and max_followers is not None:
            follower_info = {"min": min_followers, "max": max_followers, "range": raw_followers}
        elif min_followers is not None:
            follower_info = {"min": min_followers}
        
        return {
            "category": category,
            "platform": platform,
            "followers": follower_info,
            "limit": api_limit,
            "count": len(influencers),
            "influencers": influencers
        }
        
    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}