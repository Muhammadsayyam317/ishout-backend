import logging
from typing import Dict, Any
from app.services.embedding_service import query_vector_store

# Setup logging
logger = logging.getLogger(__name__)



async def search_tiktok_influencers(query: str, limit: int = 10, category: str = None, min_followers: int = None) -> Dict[str, Any]:
    """
    Search for TikTok influencers based on a query
    
    Args:
        query: The search query
        limit: Maximum number of influencers to return
        category: Optional category filter for content
        min_followers: Optional minimum follower count for proximity matching
        
    Returns:
        Dictionary containing platform and influencer data
    """
    # Log the search parameters
    logger.info(f"TikTok search with query: '{query}', limit: {limit}, category: {category}, min_followers: {min_followers}")
    
    # Directly call the vector store search - let errors propagate
    result = await query_vector_store(query, "tiktok", limit, category=category, min_followers=min_followers)
    
    # Log the results with query to verify we're getting different results for different queries
    logger.info(f"TikTok Results for query '{query}': {len(result)} influencers found")
    
    tiktok_influencers = []
    for doc in result:
        # Handle different result formats (Document objects or dictionaries)
        if isinstance(doc, dict):
            page_content = doc.get("page_content", "No content available")
            metadata = doc.get("metadata", {})
            
            # Log the original document structure to see what we're getting
            logger.info(f"TikTok document structure: {list(doc.keys()) if doc else []}")
            
            # If we have a direct MongoDB document
            if "metadata" not in doc and not metadata:
                # The document itself might be the metadata
                metadata = doc
        else:
            # Assume it's a Document object
            page_content = getattr(doc, "page_content", "No content available")
            metadata = getattr(doc, "metadata", {})
        
        # Log the metadata to see what fields are available
        logger.info(f"TikTok metadata keys: {list(metadata.keys()) if metadata else 'No metadata'}")
        
        # Calculate engagement rate string if available
        engagement_rate = "N/A"
        eng_rate = metadata.get("engagementRate", 0)
        if eng_rate:
            try:
                engagement_rate = f"{float(eng_rate) * 100:.2f}%"
            except (ValueError, TypeError):
                logger.warning(f"Invalid engagement rate value: {eng_rate}")
        
        # Try to find username from various possible fields
        username = None
        for field in ["influencer_username", "username", "uniqueId", "id"]:
            if field in metadata and metadata[field]:
                username = metadata[field]
                break
        
        # If username is still not found, try to extract it from the external link
        external_link = ""
        if "socials" in metadata and isinstance(metadata["socials"], dict):
            external_link = metadata["socials"].get("tiktok", "")
        elif "externalLink" in metadata:
            external_link = metadata["externalLink"]
        elif "url" in metadata:
            external_link = metadata["url"]
            
        if not username and external_link:
            # Extract username from URL pattern like https://www.tiktok.com/@username
            import re
            username_match = re.search(r'tiktok\.com/@?([^/]+)', external_link)
            if username_match:
                username = username_match.group(1)
        
        # Create influencer object with thorough field checking
        influencer = {
            "bio": metadata.get("bio") or metadata.get("signature") or metadata.get("description", ""),
            "name": metadata.get("name") or metadata.get("nickname") or metadata.get("title", ""),
            "influencer_username": username,
            "followers": metadata.get("followers") or metadata.get("followerCount") or 0,
            "engagement_rate": engagement_rate,
            "country": metadata.get("country") or metadata.get("region") or "",
            "pic": metadata.get("pic") or metadata.get("avatarMedium") or metadata.get("coversMedium", ""),
            "external_link": external_link or (f"https://www.tiktok.com/@{username}" if username else "")
        }
        tiktok_influencers.append(influencer)
    
    return {
        "platform": "tiktok",
        "influencers": tiktok_influencers
    }