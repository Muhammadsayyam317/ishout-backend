from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class InfluencerReference(BaseModel):
    """Model for storing influencer reference with platform info"""

    influencer_id: str
    platform: str


class CreateCampaignRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    influencer_ids: List[str] = []
    user_id: Optional[str] = None
    limit: Optional[int] = 10


class CampaignResponse(BaseModel):
    """Response model for campaign data"""

    _id: str
    name: str
    description: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    influencer_ids: List[str]  # Legacy field for backward compatibility
    influencer_references: List[InfluencerReference] = (
        []
    )  # New field with platform info
    rejected_ids: List[str] = []  # Rejected by admin
    rejectedByUser: List[str] = []  # Rejected by user
    user_id: Optional[str] = None  # User who created the campaign
    status: CampaignStatus = CampaignStatus.PENDING  # Campaign status
    limit: Optional[int] = 10  # Number of influencers to generate
    created_at: datetime
    updated_at: datetime


class ApproveSingleInfluencerRequest(BaseModel):
    """Request model to approve a single influencer into a campaign"""

    campaign_id: str
    influencer_id: str
    platform: str  # Required to know which platform the influencer belongs to


class CampaignListResponse(BaseModel):
    """Response model for campaign list"""

    campaigns: List[CampaignResponse]
    total: int


class ApproveMultipleInfluencersRequest(BaseModel):
    """Approve multiple influencers into a campaign at once"""

    campaign_id: str
    influencers: List[InfluencerReference]


class AdminGenerateInfluencersRequest(BaseModel):
    """Request model for admin to generate influencers for a campaign"""

    campaign_id: str
    limit: Optional[int] = 10  # Number of influencers to generate


class CampaignStatusUpdateRequest(BaseModel):
    """Request model to update campaign status"""

    campaign_id: str
    status: CampaignStatus


class RejectInfluencersRequest(BaseModel):
    """Request model to reject influencers and generate new ones"""

    campaign_id: str
    influencer_ids: List[str]  # List of influencer IDs to reject
    limit: Optional[int] = (
        None  # Number of new influencers to generate (optional, uses campaign's limit by default)
    )


class UserRejectInfluencersRequest(BaseModel):
    """Request model for user to reject approved influencers"""

    campaign_id: str
    influencer_ids: List[str]  # List of influencer IDs to reject
