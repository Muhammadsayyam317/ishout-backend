from typing import Dict, Any
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.services.guardrails_service import check_input_guard_rail
from app.utils.prompts import FIND_INFLUENCER_PROMPT
from app.utils.helpers import parse_follower_count



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
        
        # Parse followers if provided
        min_followers = None
        if raw_followers:
            min_followers = parse_follower_count(raw_followers)
        
        # Parse limit to integer
        try:
            api_limit = int(limit)
        except ValueError:
            api_limit = 5
        
        # Build query
        query = f"find influencers with at least {min_followers} followers"
        
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
        print(f"Searching for {category} influencers on {platform} with min_followers: {min_followers}, limit: {api_limit}")
        
        # Make the API call
        result = await tool(query=query, limit=api_limit)
        
        # Get the influencers from the result
        influencers = result.get("influencers", [])
        
        # Return simplified response
        return {
            "category": category,
            "platform": platform,
            "followers": min_followers,
            "limit": api_limit,
            "count": len(influencers),
            "influencers": influencers
        }
        
    except Exception as e:
        print(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}