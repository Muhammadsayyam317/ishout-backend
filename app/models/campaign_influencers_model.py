from enum import Enum
from pydantic import BaseModel


class CampaignInfluencerStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class CampaignInfluencersRequest(BaseModel):
    campaign_id: str
    influencer_id: str
    platform: str
    status: CampaignInfluencerStatus


class CampaignInfluencersResponse(BaseModel):
    message: str
    status: CampaignInfluencerStatus
