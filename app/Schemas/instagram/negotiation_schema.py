from enum import Enum
from typing import Optional, List
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
    reply: Optional[GenerateReplyOutput] = None

    stage: Optional[NegotiationStage] = None
    strategy: Optional[NegotiationStrategy] = None
    sender_type: Optional[SenderType] = None
