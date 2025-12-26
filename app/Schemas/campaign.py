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
    influencer_id: str
    platform: str


class CreateCampaignRequest(BaseModel):
    name: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: Optional[List[str]] = None
    country: Optional[List[str]] = None
    user_id: Optional[str] = None
    limit: Optional[int] = 10
    company_name: Optional[str] = None


class CampaignResponse(BaseModel):
    _id: str
    name: str
    description: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    user_id: Optional[str] = None
    company_name: Optional[str] = None
    status: CampaignStatus = CampaignStatus.PENDING
    limit: Optional[int] = 10
    created_at: datetime
    updated_at: datetime


class ApproveSingleInfluencerRequest(BaseModel):
    campaign_id: str
    influencer_id: str
    platform: str


class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int


class ApproveMultipleInfluencersRequest(BaseModel):
    campaign_id: str
    influencers: List[InfluencerReference]


class AdminGenerateInfluencersRequest(BaseModel):
    campaign_id: str
    limit: Optional[int] = None


class CampaignStatusUpdateRequest(BaseModel):
    campaign_id: str
    status: CampaignStatus


class RejectInfluencersRequest(BaseModel):
    campaign_id: str
    rejected_influencer_id: str
    platform: str
    category: str
    followers: int
    country: str


class UserRejectInfluencersRequest(BaseModel):
    campaign_id: str
    influencer_ids: List[str]
