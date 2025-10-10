
import logging
from typing import Tuple

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