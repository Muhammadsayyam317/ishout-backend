from enum import Enum
from typing import Dict, Literal, Optional, List, TypedDict
from pydantic import BaseModel


# ------------------ Enums ------------------
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
    # Incoming message
    user_message: str
    lastMessage: str
    # NLP / intent
    intent: Literal["interest", "rate", "availability", "reject", "unclear"]
    analysis: dict

    # Questions tracking
    askedQuestions: Dict[str, bool]  # rate, availability, interest
    # Influencer replies
    influencerResponse: Dict[str, Optional[str | float | bool]]
    # Pricing
    pricingRules: Dict[str, float]  # minPrice, maxPrice
    # Negotiation
    negotiationStatus: Literal["pending", "agreed", "rejected", "escalate"]
    # Reply
    final_reply: str
    next_action: str
    # History
    history: List[dict]
