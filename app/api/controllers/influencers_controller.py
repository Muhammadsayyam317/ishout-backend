from typing import Dict, Any, Tuple
import json
import logging
from app.tools.instagram_influencers import search_instagram_influencers
from app.tools.tiktok_influencers import search_tiktok_influencers
from app.tools.youtube_influencers import search_youtube_influencers
from app.services.guardrails_service import check_input_guard_rail
from app.utils.prompts import FIND_INFLUENCER_PROMPT

# Setup logging
logger = logging.getLogger(__name__)

def parse_follower_count(value: str) -> int:
    """
    Parse follower counts with K/M suffixes (e.g., "5K", "1.5M")
    
    Args:
        value: Follower count as string with possible K or M suffix
        
    Returns:
        Integer representation of the follower count
    """
    try:
        # If it's already a number, just return it
        if isinstance(value, (int, float)):
            return int(value)
        
        # Remove any commas or spaces
        value = value.replace(",", "").replace(" ", "").upper()
        
        # Check for K suffix
        if value.endswith("K"):
            return int(float(value[:-1]) * 1000)
        # Check for M suffix
        elif value.endswith("M"):
            return int(float(value[:-1]) * 1000000)
        # No suffix, convert to int
        else:
            return int(float(value))
    except (ValueError, TypeError):
        # Default to 0 if we can't parse
        logger.warning(f"Could not parse follower count: {value}")
        return 0

def parse_follower_range(value: str) -> Tuple[int, int, str]:
    """
    Parse follower ranges with K/M suffixes (e.g., "1K-5K", "1M-3M")
    
    Args:
        value: Follower range as string with possible K or M suffixes
        
    Returns:
        Tuple of (min_count, max_count, original_string)
    """
    try:
        if "-" not in str(value):
            # Not a range, just parse as a single value
            count = parse_follower_count(value)
            return count, count, str(value)
        
        # Split the range
        start_str, end_str = value.split("-", 1)
        start_count = parse_follower_count(start_str)
        end_count = parse_follower_count(end_str)
        
        return start_count, end_count, value
    except Exception as e:
        logger.warning(f"Error parsing follower range '{value}': {str(e)}")
        # Return default values
        return 0, 0, str(value)

class Agent:
    """Simple Agent class to mimic OpenAI's Agent functionality"""
    def __init__(self, name, tools, instructions, input_guardrails=None):
        self.name = name
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails or []
        
    async def run(self, query, limit=5):
        """Run the agent with the given query"""
        # Check guardrails
        for guardrail in self.input_guardrails:
            guardrail_result = await guardrail(query)
            if guardrail_result.get("tripwire", False):
                return {"error": True, "message": "Input does not appear to be related to influencers"}
                
        # Parse the query to determine which tool to use
        platform = "instagram"  # Default platform
        if "instagram" in query.lower():
            platform = "instagram"
            tool = search_instagram_influencers
        elif "tiktok" in query.lower():
            platform = "tiktok"
            tool = search_tiktok_influencers
        elif "youtube" in query.lower():
            platform = "youtube"
            tool = search_youtube_influencers
        else:
            # Default to Instagram
            tool = search_instagram_influencers
            
        try:
            result = await tool(query=query, limit=limit)
            return {"finalOutput": json.dumps(result)}
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            return {"error": True, "message": str(e)}

# Create the agent instance
find_influencer_agent = Agent(
    name="Find Influencer Agent",
    tools=[
        search_instagram_influencers,
        search_tiktok_influencers,
        search_youtube_influencers,
    ],
    instructions=FIND_INFLUENCER_PROMPT,
    input_guardrails=[check_input_guard_rail],
)

async def find_influencers(request_data: Dict[str, Any]):
    """Handler for the find-influencer endpoint supporting multiple values"""
    try:
        # Parse comma-separated values
        categories = [c.strip() for c in str(request_data.get("category", "")).split(",") if c.strip()]
        platforms = [p.strip() for p in str(request_data.get("platform", "")).split(",") if p.strip()]
        
        # Parse followers with support for K/M notation and ranges
        raw_followers = [f.strip() for f in str(request_data.get("followers", "")).split(",") if f.strip()]
        followers_list = []
        raw_followers_list = []  # Keep the original strings for display
        
        for f in raw_followers:
            min_count, max_count, original = parse_follower_range(f)
            # Always use the maximum count for filtering
            followers_list.append(max_count)
            raw_followers_list.append(original)
        
        # Get raw limit values without parsing - we'll pass these directly to the prompt
        raw_limits = [l.strip() for l in str(request_data.get("limit", "")).split(",") if l.strip()]
        
        # Default to 5 if no limit is provided
        if not raw_limits:
            raw_limits = ["5"]
            
        # For API calls, we need numeric values - but we'll be very liberal in what we accept
        api_limits = []
        for limit_str in raw_limits:
            try:
                if "-" in limit_str:
                    # For ranges like "2-6", use the end value for API call limit
                    # but keep the original string for the prompt
                    _, end = map(int, limit_str.split("-", 1))
                    api_limits.append(end)
                else:
                    # For single values, convert to int
                    api_limits.append(int(limit_str))
            except ValueError:
                # If conversion fails, default to 5
                api_limits.append(5)

        # Determine the number of queries to run
        max_len = max(len(categories), len(platforms), len(followers_list), len(raw_limits))
        if max_len == 0:
            return {"error": "No valid input provided."}

        # Extend lists to match max_len by repeating last value
        def extend(lst):
            return lst + [lst[-1]] * (max_len - len(lst)) if lst else [None] * max_len
        categories = extend(categories)
        platforms = extend(platforms)
        followers_list = extend(followers_list)
        raw_followers_list = extend(raw_followers_list)  # Extend the raw followers list
        raw_limits = extend(raw_limits)
        api_limits = extend(api_limits)

        all_results = []
        for i in range(max_len):
            category = categories[i]
            platform = platforms[i]
            followers = followers_list[i]  # Numeric value for filtering
            raw_followers = raw_followers_list[i]  # Original string with K/M notation
            api_limit = api_limits[i]
            
            # Get the original limit string to pass directly to the query
            limit_value = raw_limits[i]
            
            # Check if this is a range or a single value
            is_range = "-" in limit_value
            
            if is_range:
                # For range format, be very explicit about the dynamic selection
                start, end = map(int, limit_value.split("-", 1))
                query = f"Find between {start} and {end} influencers for a {category} campaign on {platform}. CRITICAL INSTRUCTION: You must dynamically decide the exact number within this range that would be most appropriate - DO NOT automatically select {end} influencers. Consider the query specificity to determine if you should return closer to {start} or closer to {end} influencers. Only include influencers who have {raw_followers} or more followers."
            else:
                # For single value
                query = f"find exactly {limit_value} influencer(s) for {category} campaign on {platform} who have more than or equal to {raw_followers} followers"
            # Select tool
            if platform.lower() == "instagram":
                tool = search_instagram_influencers
            elif platform.lower() == "tiktok":
                tool = search_tiktok_influencers
            elif platform.lower() == "youtube":
                tool = search_youtube_influencers
            else:
                tool = search_instagram_influencers
            try:
                # Make the API call with the api_limit
                result = await tool(query=query, limit=api_limit)
                
                # Get the influencers from the result
                influencers = result.get("influencers", result)
                current_count = len(influencers)
                
                # Log the results with more detailed information
                if is_range:
                    start, end = map(int, limit_value.split("-", 1))
                    logger.info(f"Range requested: {start}-{end}, Retrieved: {current_count} influencers")
                    if current_count == end:
                        logger.warning(f"Model returned the maximum number ({end}) from the range {start}-{end}. Verify dynamic selection is working correctly.")
                    elif start <= current_count < end:
                        logger.info(f"Model dynamically selected {current_count} influencers within the range {start}-{end} as requested.")
                else:
                    logger.info(f"Exact count requested: {limit_value}, Retrieved: {current_count} influencers")
                    
                # Create the result item with the original limit value and follower display
                result_item = {
                    "category": category,
                    "platform": platform,
                    "followers": followers,  # Numeric value for filtering
                    "followers_display": raw_followers,  # Original string with K/M suffix
                    "limit": limit_value,
                }
                
                # Add range information if applicable for limit
                if is_range:
                    try:
                        start, end = map(int, limit_value.split("-", 1))
                        result_item["range_min"] = start
                        result_item["range_max"] = end
                        
                        # Add range satisfaction status
                        count = len(influencers)
                        if start <= count <= end:
                            result_item["range_status"] = "satisfied"
                        elif count < start:
                            result_item["range_status"] = f"insufficient (found {count}, requested {limit_value})"
                        else:
                            result_item["range_status"] = f"exceeded (found {count}, requested {limit_value})"
                    except ValueError:
                        # If we can't parse the range for some reason, just continue without range info
                        pass
                
                # Add follower range information if applicable
                if "-" in str(raw_followers):
                    try:
                        min_followers, max_followers, _ = parse_follower_range(raw_followers)
                        result_item["followers_min"] = min_followers
                        result_item["followers_max"] = max_followers
                    except Exception:
                        # If we can't parse the range, continue without follower range info
                        pass
                
                result_item["data"] = influencers
                result_item["count"] = len(influencers)
                
                all_results.append(result_item)
            except Exception as e:
                # Construct the error response
                error_item = {
                    "category": category,
                    "platform": platform,
                    "followers": followers,
                    "followers_display": raw_followers,  # Original string with K/M suffix
                    "limit": limit_value,
                    "error": str(e)
                }
                
                # Add range information if applicable for limit
                if is_range:
                    try:
                        start, end = map(int, limit_value.split("-", 1))
                        error_item["range_min"] = start
                        error_item["range_max"] = end
                    except ValueError:
                        # If we can't parse the range, continue without range info
                        pass
                        
                # Add follower range information if applicable
                if "-" in str(raw_followers):
                    try:
                        min_followers, max_followers, _ = parse_follower_range(raw_followers)
                        error_item["followers_min"] = min_followers
                        error_item["followers_max"] = max_followers
                    except Exception:
                        # If we can't parse the range, continue without follower range info
                        pass
                
                all_results.append(error_item)
        return {"results": all_results}
    except Exception as e:
        logger.error(f"Error in find_influencers: {str(e)}")
        return {"error": str(e)}