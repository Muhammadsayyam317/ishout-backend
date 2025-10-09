import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.services.embedding_service import query_vector_store

# Setup logging
logger = logging.getLogger(__name__)

class InstagramInfluencerQueryParams(BaseModel):
    """Parameters for Instagram influencer search"""
    query: str = Field(..., description="The query to search influencers for")
    limit: Optional[int] = Field(10, description="The maximum number of influencers to return")

class InstagramInfluencer(BaseModel):
    """Model for Instagram influencer data"""
    content: str
    influencer_username: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    followers: Optional[int] = None
    engagement_rate: Optional[str] = None
    pic: Optional[str] = None
    external_link: Optional[str] = None

class InstagramInfluencerResponse(BaseModel):
    """Response model for Instagram influencer search"""
    platform: str = "instagram"
    influencers: List[InstagramInfluencer]

async def search_instagram_influencers(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for Instagram influencers based on a query
    
    Args:
        query: The search query
        limit: Maximum number of influencers to return
        
    Returns:
        Dictionary containing platform and influencer data
    """
    try:
        result = await query_vector_store(query, "instagram", limit)
        logger.info(f"Instagram Results: {len(result)} influencers found")
        
        instagram_influencers = []
        for doc in result:
            # Handle different result formats (Document objects or dictionaries)
            if isinstance(doc, dict):
                page_content = doc.get("page_content", "No content available")
                metadata = doc.get("metadata", {})
                
                # Log the original document structure to see what we're getting
                logger.info(f"Instagram document structure: {list(doc.keys()) if doc else []}")
                
                # If we have a direct MongoDB document (fallback method)
                if "metadata" not in doc and not metadata:
                    # The document itself might be the metadata
                    metadata = doc
            else:
                # Assume it's a Document object
                page_content = getattr(doc, "page_content", "No content available")
                metadata = getattr(doc, "metadata", {})
            
            # Log the metadata to see what fields are available
            logger.info(f"Instagram metadata keys: {list(metadata.keys()) if metadata else 'No metadata'}")
            
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
        
        return {
            "platform": "instagram",
            "influencers": instagram_influencers
        }
    except Exception as e:
        logger.error(f"Error in search_instagram_influencers: {str(e)}")
        return {
            "error": True,
            "message": str(e) or "Unknown error occurred while searching Instagram influencers"
        }