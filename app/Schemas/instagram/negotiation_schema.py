from datetime import datetime
from enum import Enum
from typing import Dict, Literal, Optional, List
from typing_extensions import TypedDict


class NextAction(str, Enum):
    ANSWER_QUESTION = "answer_question"
    ASK_INTEREST = "ask_interest"
    ASK_RATE = "ask_rate"
    ASK_AVAILABILITY = "ask_availability"
    CONFIRM_PRICING = "confirm_pricing"
    CONFIRM_DELIVERABLES = "confirm_deliverables"
    CONFIRM_TIMELINE = "confirm_timeline"
    GENERATE_CLARIFICATION = "generate_clarification"
    GENERATE_REJECTION = "generate_rejection"
    ESCALATE_NEGOTIATION = "escalate_negotiation"
    REJECT_NEGOTIATION = "reject_negotiation"
    ACCEPT_NEGOTIATION = "accept_negotiation"
    CLOSE_CONVERSATION = "close_conversation"
    WAIT_OR_ACKNOWLEDGE = "wait_or_acknowledge"


class MessageIntent(str, Enum):
    INTEREST = "interest"
    RATE = "rate"
    AVAILABILITY = "availability"
    DELIVERABLES = "deliverables"
    TIMELINE = "timeline"
    REJECT = "reject"
    ACCEPT = "accept"
    UNCLEAR = "unclear"


class AnalyzeMessageOutput(TypedDict):
    intent: MessageIntent
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
    next_action: NextAction


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
    last_message: str

    intent: MessageIntent
    analysis: AnalyzeMessageOutput

    asked_questions: Dict[str, bool]
    influencer_response: Dict[str, Optional[str | float | bool]]

    pricing_rules: PricingRules
    negotiation_status: Literal[
        "pending",
        "agreed",
        "rejected",
        "escalated",
    ]
    next_action: NextAction
    final_reply: str

    history: List[dict]
    manual_negotiation: bool
    final_rate: Optional[float]


class InfluencerDetails(TypedDict):
    requested_rate: float
    min_price: float
    max_price: float
    final_rate: Optional[float]
    last_updated: datetime
    agreed_rate: Literal["system", "manual"]
    negotiation_status: Literal["confirmed", "manual required", "replaced"]
    human_escalation_required: bool
