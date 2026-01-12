from enum import Enum
from pydantic import BaseModel


class NegotiationStage(Enum):
    INITIAL = "INITIAL"
    COUNTER = "COUNTER"
    FINAL = "FINAL"


class NegotiationStrategy(Enum):
    SOFT = "SOFT"
    VALUE_BASED = "VALUE_BASED"
    WALK_AWAY = "WALK_AWAY"


class AnalyzeMessageResult(BaseModel):
    brand_intent: str
    pricing_mentioned: bool
    campaign_details_missing: bool
    next_action: str
    negotiation_stage: NegotiationStage = NegotiationStage.INITIAL
    negotiation_strategy: NegotiationStrategy = NegotiationStrategy.SOFT
    ai_draft: str = ""
    human_approved: bool | None = None
