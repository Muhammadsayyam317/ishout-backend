from enum import Enum
from typing import Optional, List, TypedDict
from pydantic import BaseModel


# ------------------ Enums ------------------
class NextAction(str, Enum):
    ANSWER_QUESTION = "ANSWER_QUESTION"
    ASK_AVAILABILITY = "ASK_AVAILABILITY"
    ASK_RATE = "ASK_RATE"
    ASK_INTEREST = "ASK_INTEREST"
    CONFIRM = "CONFIRM"


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


# ------------------ Influencer Details Input ------------------
class InfluencerDetailsInput(BaseModel):
    rate: float
    currency: str
    content_type: str
    content_format: str
    content_length: int
    content_duration: int
    availability: str


# ------------------ Generate Reply Output ------------------
class GenerateReplyOutput(BaseModel):
    final_reply: str


# ------------------ Conversation State ------------------
class InstagramConversationState(TypedDict):
    thread_id: str
    user_message: str
    analysis: AnalyzeMessageOutput
    availability: str
    rate: float
    currency: str
    interest: bool
    influencer_details: InfluencerDetailsInput
    final_reply: str
    next_action: NextAction
    influencer_id: str
    campaign_id: str
