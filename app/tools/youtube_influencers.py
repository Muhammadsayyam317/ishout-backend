from typing import Dict, Any
from app.services.embedding_service import query_vector_store


async def search_youtube_influencers(query: str, limit: int = 10, min_followers: int = None, max_followers: int = None) -> Dict[str, Any]:
    """
    Search for YouTube influencers based on a query
    
    Args:
        query: The search query
        limit: Maximum number of influencers to return
        min_followers: Minimum follower count for filtering (optional)
        max_followers: Maximum follower count for filtering (optional)
        
    Returns:
        Dictionary containing platform and influencer data
    """
    # Search for YouTube influencers
    print(f"YouTube search: '{query}' (limit: {limit})")
    
    result = await query_vector_store(query, "youtube", limit, min_followers, max_followers)
    print(f"Found {len(result)} YouTube influencers")
    
    youtube_influencers = []
    for doc in result:
        # Handle different result formats (Document objects or dictionaries)
        if isinstance(doc, dict):
            page_content = doc.get("page_content", "No content")
            metadata = doc.get("metadata", {})
            
            # Print the document structure for debugging
            print(f"YouTube doc structure: {list(doc.keys()) if doc else []}")
            
            # If we have a direct MongoDB document
            if "metadata" not in doc and not metadata:
                # The document itself might be the metadata
                metadata = doc
        else:
            # Assume it's a Document object
            page_content = getattr(doc, "page_content", "No content")
            metadata = getattr(doc, "metadata", {})
        
        # Print what metadata we're working with
        print(f"YouTube metadata keys: {list(metadata.keys()) if metadata else 'No metadata'}")
        
        # Calculate engagement rate string if available
        engagement_rate = "N/A"
        eng_rate = metadata.get("engagementRate", 0)
        if eng_rate:
            try:
                engagement_rate = f"{float(eng_rate) * 100:.2f}%"
            except (ValueError, TypeError):
                print(f"Invalid engagement rate value: {eng_rate}")
        
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
            "external_link": external_link
        }
        youtube_influencers.append(influencer)
    
    return {
        "platform": "youtube",
        "influencers": youtube_influencers
    }