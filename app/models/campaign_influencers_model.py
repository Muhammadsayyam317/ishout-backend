from enum import Enum
from pydantic import BaseModel


class CampaignInfluencerStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class CampaignInfluencersRequest(BaseModel):
    campaign_id: str
    influencer_id: str
    username: str
    picture: str
    engagementRate: float
    bio: str
    platform: str
    followers: int
    country: str
    status: CampaignInfluencerStatus
    admin_approved: bool = False
    company_approved: bool = False
    # user_id: str = None


class CampaignInfluencersResponse(BaseModel):
    message: str
    status: CampaignInfluencerStatus
