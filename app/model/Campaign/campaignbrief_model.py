from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from bson import ObjectId
from app.Schemas.campaign_influencers import CampaignBriefResponse


class CampaignBriefStatus(str, Enum):
    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"
    REGENERATED = "regenerated"


class CampaignBriefGeneration(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    company_id: Optional[str] = None
    prompt: str
    response: CampaignBriefResponse
    version: int = 1
    regenerated_from: Optional[str] = None
    status: CampaignBriefStatus = CampaignBriefStatus.PENDING
    is_user_edited: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda oid: str(oid),
            datetime: lambda dt: dt.isoformat(),
        }
