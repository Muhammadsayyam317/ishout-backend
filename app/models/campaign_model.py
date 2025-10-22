from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class InfluencerReference(BaseModel):
    """Model for storing influencer reference with platform info"""
    influencer_id: str
    platform: str


class CreateCampaignRequest(BaseModel):
    """Request model to create a new campaign"""
    name: Optional[str] = None
    description: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    influencer_ids: List[str] = []  # Initially empty, populated when influencers are approved


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
    influencer_references: List[InfluencerReference] = []  # New field with platform info
    rejected_ids: List[str] = []
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
