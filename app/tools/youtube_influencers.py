import logging
from typing import Dict, Any
from app.services.embedding_service import query_vector_store


# Setup logging
logger = logging.getLogger(__name__)


async def search_youtube_influencers(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for YouTube influencers based on a query
    
    Args:
        query: The search query
        limit: Maximum number of influencers to return
        
    Returns:
        Dictionary containing platform and influencer data
    """
    # Log the search parameters
    logger.info(f"YouTube search with query: '{query}', limit: {limit}")
    
    # Directly call the vector store search - let errors propagate
    result = await query_vector_store(query, "youtube", limit)
    
    # Log the search results with query to verify we're getting different results for different queries
    logger.info(f"YouTube Results for query '{query}': {len(result)} influencers found")
    
    youtube_influencers = []
    for doc in result:
        # Handle different result formats (Document objects or dictionaries)
        if isinstance(doc, dict):
            page_content = doc.get("page_content", "No content")
            metadata = doc.get("metadata", {})
            
            # Log the document structure for debugging
            logger.info(f"YouTube doc structure: {list(doc.keys()) if doc else []}")
            
            # If we have a direct MongoDB document
            if "metadata" not in doc and not metadata:
                # The document itself might be the metadata
                metadata = doc
        else:
            # Assume it's a Document object
            page_content = getattr(doc, "page_content", "No content")
            metadata = getattr(doc, "metadata", {})
        
        # Log what metadata we're working with
        logger.info(f"YouTube metadata keys: {list(metadata.keys()) if metadata else 'No metadata'}")
        
        # Calculate engagement rate string if available
        engagement_rate = "N/A"
        eng_rate = metadata.get("engagementRate", 0)
        if eng_rate:
            try:
                engagement_rate = f"{float(eng_rate) * 100:.2f}%"
            except (ValueError, TypeError):
                logger.warning(f"Invalid engagement rate value: {eng_rate}")
        
        # Try to extract username from various fields
        username = None
        for field in ["influencer_username", "username", "channelId", "channelTitle", "id"]:
            if field in metadata and metadata[field]:
                username = metadata[field]
                break
            
        # Try to extract external link
        external_link = ""
        if "socials" in metadata and isinstance(metadata["socials"], dict):
            external_link = metadata["socials"].get("youtube", "")
        elif "externalLink" in metadata:
            external_link = metadata["externalLink"]
        elif "url" in metadata:
            external_link = metadata["url"]
        
        # If we have a username but no external link, construct one
        if username and not external_link:
            external_link = f"https://www.youtube.com/channel/{username}"
        
        # Create influencer object with thorough field checking
        influencer = {
            "bio": metadata.get("bio") or metadata.get("description") or metadata.get("snippet", {}).get("description", ""),
            "name": metadata.get("name") or metadata.get("title") or metadata.get("snippet", {}).get("title", ""),
            "influencer_username": username,
            "followers": metadata.get("followers") or metadata.get("subscriberCount") or metadata.get("statistics", {}).get("subscriberCount", 0),
            "engagement_rate": engagement_rate,
            "country": metadata.get("country") or metadata.get("snippet", {}).get("country", ""),
            "pic": metadata.get("pic") or metadata.get("thumbnail") or metadata.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url", ""),
            "external_link": external_link,
            "similarity": doc.get("similarity") if isinstance(doc, dict) and "similarity" in doc else None
        }
        youtube_influencers.append(influencer)
    
    return {
        "platform": "youtube",
        "influencers": youtube_influencers
    }