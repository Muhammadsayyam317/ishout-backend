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
    engagementRate: str
    bio: str
    platform: str
    followers: str
    country: str
    status: CampaignInfluencerStatus


class CampaignInfluencersResponse(BaseModel):
    message: str
    status: CampaignInfluencerStatus
