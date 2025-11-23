from pydantic import BaseModel
from typing import List, Optional


class FindInfluencerRequest(BaseModel):
    campaign_id: str
    user_id: str
    limit: Optional[int] = 10
    more: Optional[int] = None
    exclude_ids: Optional[List[str]] = None


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


class GenerateInfluencersRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    limit: str
