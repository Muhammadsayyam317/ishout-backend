from datetime import datetime, timezone
from typing import Optional
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
    admin_approved: bool = False
    company_approved: bool = False
    company_user_id: str
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
