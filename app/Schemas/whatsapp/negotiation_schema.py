from enum import Enum
from typing import Literal, Optional
from typing_extensions import TypedDict
from datetime import datetime
from app.Schemas.instagram.negotiation_schema import NextAction


class WhatsappMessageIntent(str, Enum):
    INTEREST = "interest"
    NEGOTIATE = "negotiate"
    REJECT = "reject"
    ACCEPT = "accept"
    QUESTION = "question"
    UNCLEAR = "unclear"


class WhatsappNegotiationInitialMessageRequest(TypedDict):
    to: str
    influencer_name: str
    campaign_name: str


class WhatsappNegotiationState(TypedDict):
    thread_id: str
    influencer_id: str
    user_message: str

    intent: WhatsappMessageIntent
    next_action: NextAction
    analysis: dict

    min_price: Optional[float]
    max_price: Optional[float]

    final_reply: Optional[str]


class InfluencersNegotiation(TypedDict):
    requested_rate: float
    username: str
    platform: str
    phone_number: str
    min_price: float
    max_price: float
    agreed_rate: Optional[float]
    agreed_by: Literal["AI", "Human"]
    negotiation_status: Literal[
        "Confirmed",
        "Manual Required",
        "Replaced",
    ]
    human_escalation_required: bool


class storemessage(TypedDict):
    message: str
    timestamp: datetime
    thread_id: str
    campaign_id: str
    influencer_id: str
    platform: str
    username: str
    message_type: Literal["text", "image", "video", "audio", "document"]
    mode: Literal["ai", "human"]
