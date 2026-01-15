from enum import Enum
from typing import Optional
from pydantic import BaseModel

from app.Schemas.instagram.message_schema import AnalyzeMessageOutput


class NegotiationStage(str, Enum):
    INITIAL = "INITIAL"
    COUNTER = "COUNTER"
    FINAL = "FINAL"


class NegotiationStrategy(str, Enum):
    SOFT = "SOFT"
    VALUE_BASED = "VALUE_BASED"
    WALK_AWAY = "WALK_AWAY"


class InstagramConversationState(BaseModel):
    thread_id: str
    user_message: str
    last_messages: list[str] = []
    analysis: Optional[AnalyzeMessageOutput]
    final_reply: Optional[str]
