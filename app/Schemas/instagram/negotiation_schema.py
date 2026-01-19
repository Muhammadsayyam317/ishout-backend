from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

# ------------------ Enums ------------------


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


class NextAction(str, Enum):
    ANSWER_QUESTION = "ANSWER_QUESTION"
    ASK_AVAILABILITY = "ASK_AVAILABILITY"
    ASK_RATE = "ASK_RATE"
    ASK_INTEREST = "ASK_INTEREST"
    CONFIRM = "CONFIRM"


# ------------------ Conversation State ------------------


class InstagramConversationState(BaseModel):
    thread_id: str
    user_message: str
    analysis: Optional["AnalyzeMessageOutput"] = None
    availability: Optional[str] = None
    rate: Optional[float] = None
    currency: Optional[str] = None
    interest: Optional[bool] = None
    final_reply: Optional[str] = None
    next_action: Optional[NextAction] = None
    influencer_id: Optional[str] = None
    campaign_id: Optional[str] = None


# ------------------ Analyze Message Output ------------------


class AnalyzeMessageOutput(BaseModel):
    intent: str
    is_question: bool
    question_topic: Optional[str] = None
    pricing_mentioned: bool
    budget_amount: Optional[float] = None
    currency: Optional[str] = None
    availability_mentioned: bool
    interest_mentioned: bool
    missing_required_details: List[str]
    recommended_next_action: str


# ------------------ Generate Reply Output ------------------


class GenerateReplyOutput(BaseModel):
    final_reply: str


# ------------------ Influencer Details Input ------------------


class InfluencerDetailsInput(BaseModel):
    rate: float
    currency: str
    content_type: str
    content_format: str
    content_length: int
    content_duration: int
    availability: str
