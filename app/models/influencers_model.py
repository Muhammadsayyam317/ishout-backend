from pydantic import BaseModel
from typing import List, Optional

class FindInfluencerRequest(BaseModel):
    """Simplified request model - only requires campaign_id and user_id"""
    campaign_id: str
    user_id: str
    limit: Optional[int] = 10  # Number of influencers to find
    more: Optional[int] = None  # Override limit for subsequent calls
    exclude_ids: Optional[List[str]] = None  # IDs to exclude from results


class FindInfluencerLegacyRequest(BaseModel):
    """Legacy request model for backward compatibility"""
    platform: List[str]
    category: List[str]
    followers: List[str]
    limit: str
    country: List[str]
    # Optional: request a new batch size overriding limit for subsequent calls
    more: Optional[int] = None
    # Optional: IDs/handles/urls already seen or accepted; ensure fresh results only
    exclude_ids: Optional[List[str]] = None
    # Optional: campaign details for auto-creation
    campaign_name: Optional[str] = None
    campaign_description: Optional[str] = None
    is_campaign_create: Optional[bool] = False
    # Optional: link search context to an existing campaign
    campaign_id: Optional[str] = None


class DeleteInfluencerRequest(BaseModel):
    """Request model to delete influencer data and embeddings from a platform collection.

    Provide at least one identifier. If multiple are provided, they are combined with OR.
    """
    platform: str
    influencer_id: str


class MoreInfluencerRequest(BaseModel):
    """Simplified request model for fetching more influencers"""
    campaign_id: str
    user_id: str
    more: int  # Number of additional influencers to fetch
    exclude_ids: List[str]  # IDs to exclude from results


class MoreInfluencerLegacyRequest(BaseModel):
    """Legacy request model for fetching more (fresh) influencers"""
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    more: int
    exclude_ids: List[str]
    # Optional: campaign context and newly rejected IDs from the last batch
    campaign_id: Optional[str] = None
