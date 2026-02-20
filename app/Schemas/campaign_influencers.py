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


class CampaignBriefResponse(BaseModel):
    Brand_Name_Influencer_Campaign_Brief: List[str]
    Campaign_Overview: List[str]
    Campaign_Objectives: List[str]
    Target_Audience: List[str]
    Influencer_Profile: List[str]
    Key_Campaign_Message: List[str]
    Content_Direction: List[str]
    Deliverables_Per_Influencer: List[str]
    Hashtags_and_Mentions: List[str]
    Timeline: List[str]
    Approval_Process: List[str]
    KPIs_and_Success_Metrics: List[str]
    Usage_Rights: List[str]
    Dos_and_Donts: List[str]
