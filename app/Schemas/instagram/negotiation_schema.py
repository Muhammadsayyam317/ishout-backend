from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field

from app.Schemas.instagram.message_schema import (
    AnalyzeMessageOutput,
    GenerateReplyOutput,
)


class NegotiationStage(str, Enum):
    INITIAL = "INITIAL"
    COUNTER = "COUNTER"
    FINAL = "FINAL"


class NegotiationStrategy(str, Enum):
    SOFT = "SOFT"
    VALUE_BASED = "VALUE_BASED"
    WALK_AWAY = "WALK_AWAY"


class SenderType(str, Enum):
    USER = "USER"
    AI = "AI"


class InstagramConversationState(BaseModel):
    thread_id: str
    user_message: str

    analysis: Optional[AnalyzeMessageOutput] = None

    availability: Optional[str] = None
    rate: Optional[float] = None
    currency: Optional[str] = None
    interest: Optional[bool] = None

    final_reply: Optional[str] = None
    next_action: Optional[str] = None

    class InstagramConversatuinResponse(BaseModel):
        _id: ObjectId
        thread_id: str
        platform: str
        influencer_id: str
        campaign_id: str
        company_user_id: str
        min_price: int
        max_price: int
        currency: str
        negotiation_stage: NegotiationStage
        negotiation_strategy: NegotiationStrategy
        ai_enabled: bool
        created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
        updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))
