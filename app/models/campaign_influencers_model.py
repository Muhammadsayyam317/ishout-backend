from enum import Enum
from typing import Optional
from pydantic import BaseModel


class CampaignInfluencerStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


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


class CampaignInfluencersResponse(BaseModel):
    message: str
    status: CampaignInfluencerStatus
