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

    last_messages: List[str] = Field(default_factory=list)

    analysis: Optional[AnalyzeMessageOutput] = None
    reply: Optional[str]

    influencer_id: Optional[str] = None
    campaign_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    stage: Optional[NegotiationStage] = None
    strategy: Optional[NegotiationStrategy] = None
    sender_type: Optional[SenderType] = None
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
