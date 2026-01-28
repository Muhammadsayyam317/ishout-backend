from enum import Enum
from typing import Dict, Literal, Optional, List, TypedDict


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


class AnalyzeMessageOutput(TypedDict):
    intent: str
    pricing_mentioned: bool
    budget_amount: Optional[float]
    currency: Optional[str]
    deliverables_mentioned: bool
    deliverables: Optional[str]
    timeline_mentioned: bool
    timeline: Optional[str]
    platforms_mentioned: bool
    platforms: Optional[List[str]]
    usage_rights_mentioned: bool
    exclusivity_mentioned: bool
    missing_required_details: List[str]
    recommended_next_action: str


class InfluencerDetailsInput(TypedDict):
    rate: float
    availability: str
    exclusivity: str
    usage_rights: str
    platforms: List[str]
    deliverables: str
    timeline: str


class GenerateReplyOutput(TypedDict):
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
