from enum import Enum
from typing import Dict, Literal, Optional, List, TypedDict
from pydantic import BaseModel


class NextAction(str, Enum):
    ANSWER_QUESTION = "answer_question"
    ASK_AVAILABILITY = "ask_availability"
    ASK_RATE = "ask_rate"
    ASK_INTEREST = "ask_interest"
    CONFIRM_PRICING = "confirm_pricing"
    CONFIRM_DELIVERABLES = "confirm_deliverables"
    CONFIRM_TIMELINE = "confirm_timeline"
    REJECT_NEGOTIATION = "reject_negotiation"
    ESCALATE_NEGOTIATION = "escalate_negotiation"
    REJECT_DELIVERABLES = "reject_deliverables"
    ESCALATE_DELIVERABLES = "escalate_deliverables"
    CLOSE_NEGOTIATION = "close_negotiation"
    CLOSE_CONVERSATION = "close_conversation"
    WAIT_OR_ACKNOWLEDGE = "wait_or_acknowledge"
    GENERATE_REJECTION = "generate_rejection"
    GENERATE_CLARIFICATION = "generate_clarification"


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


class InfluencerDetailsInput(BaseModel):
    rate: float
    currency: str
    content_type: str
    content_format: str
    content_length: int
    content_duration: int
    availability: str


class GenerateReplyOutput(BaseModel):
    final_reply: str


class PricingRules(TypedDict, total=False):
    minPrice: float
    maxPrice: float


class AskedQuestions(TypedDict, total=False):
    rate: bool
    availability: bool
    interest: bool


class InfluencerResponse(TypedDict, total=False):
    rate: Optional[float]
    availability: Optional[str]
    interest: Optional[bool]


class NegotiationStrategy(str, Enum):
    SOFT = "soft"
    VALUE_BASED = "value_based"


class InstagramConversationState(TypedDict):

    thread_id: str
    convoId: str
    influencer_id: str
    campaign_id: str
    user_message: str
    lastMessage: str
    intent: Literal["interest", "rate", "availability", "reject", "unclear"]
    analysis: dict

    askedQuestions: Dict[str, bool]
    influencerResponse: Dict[str, Optional[str | float | bool]]
    pricingRules: Dict[str, float]
    negotiationStatus: Literal["pending", "agreed", "rejected", "escalate"]
    final_reply: str
    next_action: str
    history: List[dict]
