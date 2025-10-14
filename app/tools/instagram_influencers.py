from typing import Dict, Any
from app.services.embedding_service import query_vector_store


async def search_instagram_influencers(query: str, limit: int = 10, min_followers: int = None, max_followers: int = None, country: str = None) -> Dict[str, Any]:
    """
    Search for Instagram influencers based on query
    
    Args:
        query: The search query
        limit: Maximum number of influencers to return
        min_followers: Minimum follower count for filtering (optional)
        max_followers: Maximum follower count for filtering (optional)
        
    Returns:
        Dictionary containing platform and influencer data
    """
    # Search for Instagram influencers
    print(f"Instagram search: '{query}' (limit: {limit})")
    
    try:
        result = await query_vector_store(query, "instagram", limit, min_followers, max_followers, country)
        print(f"Found {len(result)} Instagram influencers")
    except Exception as e:
        print(f"Instagram search error: {str(e)}")
        result = []
    
    instagram_influencers = []
    for doc in result:
        # Handle different result formats (Document objects or dictionaries)
        if isinstance(doc, dict):
            page_content = doc.get("page_content", "No content available")
            metadata = doc.get("metadata", {})
            
            # If we have a direct MongoDB document
            if "metadata" not in doc and not metadata:
                # The document itself might be the metadata
                metadata = doc
        else:
            # Assume it's a Document object
            page_content = getattr(doc, "page_content", "No content available")
            metadata = getattr(doc, "metadata", {})
        
        # Calculate engagement rate string if available
        engagement_rate = "N/A"
        eng_rate = metadata.get("engagementRate", 0)
        if eng_rate:
            try:
                engagement_rate = f"{float(eng_rate) * 100:.2f}%"
            except (ValueError, TypeError):
                engagement_rate = "N/A"
        
        # Try to find username from various possible fields
        username = None
        for field in ["influencer_username", "username", "login", "handle", "id"]:
            if field in metadata and metadata[field]:
                username = metadata[field]
                break
        
        # If username is still not found, try to extract it from the external link
        external_link = ""
        if "socials" in metadata and isinstance(metadata["socials"], dict):
            external_link = metadata["socials"].get("instagram", "")
        elif "externalLink" in metadata:
            external_link = metadata["externalLink"]
        elif "url" in metadata:
            external_link = metadata["url"]
            
        if not username and external_link:
            # Extract username from URL pattern like https://www.instagram.com/username
            import re
            username_match = re.search(r'instagram\.com/([^/]+)', external_link)
            if username_match:
                username = username_match.group(1)
        
        # Create influencer object with thorough field checking
        influencer = {
            "content": page_content,
            "influencer_username": username,
            "name": metadata.get("name") or metadata.get("full_name") or "",
            "bio": metadata.get("bio") or metadata.get("biography") or "",
            "country": metadata.get("country") or metadata.get("location") or "",
            "followers": metadata.get("followers") or metadata.get("follower_count") or metadata.get("edge_followed_by", {}).get("count", 0),
            "engagement_rate": engagement_rate,
            "pic": metadata.get("pic") or metadata.get("profile_pic_url") or metadata.get("profile_pic_url_hd", ""),
            "external_link": external_link or (f"https://www.instagram.com/{username}" if username else "")
        }
        instagram_influencers.append(influencer)
    
    result_dict = {
        "platform": "instagram",
        "influencers": instagram_influencers
    }
    if not instagram_influencers:
        result_dict["message"] = "No data available for this selection"
    return result_dict