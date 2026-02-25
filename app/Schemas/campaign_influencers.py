from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.utils.Enums.status_enum import (
    CampaignInfluencerStatus,
    GeneratedInfluencersStatus,
)


class CampaignInfluencersRequest(BaseModel):
    campaign_id: str
    influencer_id: str
    username: Optional[str] = None
    picture: Optional[str] = None
    engagementRate: Optional[float] = None
    bio: Optional[str] = None
    platform: Optional[str] = None
    followers: Optional[int] = None
    country: Optional[str] = None
    status: CampaignInfluencerStatus
    admin_approved: Optional[bool] = None
    company_approved: Optional[bool] = None
    company_user_id: Optional[str] = None
    pricing: Optional[float] = None


class CampaignInfluencersResponse(BaseModel):
    message: str
    status: CampaignInfluencerStatus


class GeneratedInfluencersRequest(BaseModel):
    campaign_id: str

    username: Optional[str] = None
    picture: Optional[str] = None
    engagementRate: Optional[float] = None
    bio: Optional[str] = None
    platform: Optional[str] = None
    followers: Optional[int] = None
    country: Optional[str] = None

    status: GeneratedInfluencersStatus = GeneratedInfluencersStatus.GENERATED

    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))


class GeneratedInfluencersResponse(BaseModel):
    message: str
    status: GeneratedInfluencersStatus


class CampaignBriefRequest(BaseModel):
    user_input: str
    user_id: str


class CampaignBriefResponse(BaseModel):
    id: Optional[str] = None 
    title: str
    brand_name_influencer_campaign_brief: str
    campaign_overview: List[str]
    campaign_objectives: List[str]
    target_audience: List[str]
    influencer_profile: List[str]
    key_campaign_message: List[str]
    content_direction: List[str]
    deliverables_per_influencer: List[str]
    hashtags_mentions: List[str]
    timeline: List[str]
    approval_process: List[str]
    kpis_success_metrics: List[str]
    usage_rights: List[str]
    dos_donts: List[str]

class CampaignBriefDBResponse(BaseModel):
    id: str
    user_id: str
    prompt: str
    response: CampaignBriefResponse
    status: str
    version: int
    regenerated_from: Optional[str] = None
    created_at: Optional[datetime] = None

class UpdateCampaignBriefRequest(BaseModel):
    campaign_overview: Optional[List[str]] = None
    campaign_objectives: Optional[List[str]] = None
    target_audience: Optional[List[str]] = None
    influencer_profile: Optional[List[str]] = None
    key_campaign_message: Optional[List[str]] = None
    content_direction: Optional[List[str]] = None
    deliverables_per_influencer: Optional[List[str]] = None
    hashtags_mentions: Optional[List[str]] = None
    timeline: Optional[List[str]] = None
    approval_process: Optional[List[str]] = None
    kpis_success_metrics: Optional[List[str]] = None
    usage_rights: Optional[List[str]] = None
    dos_donts: Optional[List[str]] = None