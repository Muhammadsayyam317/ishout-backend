from pydantic import BaseModel
from typing import List, Optional


class FindInfluencerRequest(BaseModel):
    campaign_id: str
    user_id: str
    limit: int


class FindInfluencerLegacyRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    limit: str
    country: List[str]
    more: Optional[int] = None
    exclude_ids: Optional[List[str]] = None
    campaign_name: Optional[str] = None
    campaign_description: Optional[str] = None
    is_campaign_create: Optional[bool] = False
    campaign_id: Optional[str] = None


class DeleteInfluencerRequest(BaseModel):
    platform: str
    influencer_id: str


class MoreInfluencerRequest(BaseModel):
    campaign_id: str
    user_id: str
    more: int
    exclude_ids: List[str]


class MoreInfluencerLegacyRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    more: int
    exclude_ids: List[str]
    campaign_id: Optional[str] = None


class GenerateInfluencersRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    limit: int
