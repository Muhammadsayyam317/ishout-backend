from enum import Enum
from typing import Optional
from pydantic import BaseModel


class NegotiationStage(str, Enum):
    INITIAL = "INITIAL"
    COUNTER = "COUNTER"
    FINAL = "FINAL"


class NegotiationStrategy(str, Enum):
    SOFT = "SOFT"
    VALUE_BASED = "VALUE_BASED"
    WALK_AWAY = "WALK_AWAY"


class InstagramConversationState(BaseModel):
    # Required at entry
    thread_id: str
    user_message: str

    # Filled by analyze node
    brand_intent: Optional[str] = None
    pricing_mentioned: bool = False

    negotiation_stage: NegotiationStage = NegotiationStage.INITIAL
    negotiation_strategy: NegotiationStrategy = NegotiationStrategy.SOFT

    # Filled later
    ai_draft: Optional[str] = None
    final_reply: Optional[str] = None
