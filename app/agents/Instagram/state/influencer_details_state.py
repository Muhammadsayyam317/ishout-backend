from typing import Optional, TypedDict

from pydantic import BaseModel
from app.Schemas.instagram.negotiation_schema import (
    AnalyzeMessageOutput,
    InfluencerDetailsInput,
    NextAction,
)


class AskedQuestions(TypedDict, total=False):
    rate: bool
    availability: bool
    interest: bool


class InfluencerResponse(TypedDict, total=False):
    rate: float
    availability: str
    interest: bool


class PricingRules(TypedDict, total=False):
    minPrice: float
    maxPrice: float


class ConversationState(TypedDict, total=False):
    influencerId: str
    convoId: str
    lastMessage: str
    intent: str  # interest | rate | availability | reject | unclear
    askedQuestions: AskedQuestions
    influencerResponse: InfluencerResponse
    pricingRules: PricingRules
    negotiationStatus: str  # pending | agreed | rejected | escalate
    history: list[dict]


class InstagramConversationState(BaseModel):
    thread_id: str
    user_message: str
    analysis: Optional[AnalyzeMessageOutput] = None
    availability: Optional[str] = None
    rate: Optional[float] = None
    currency: Optional[str] = None
    interest: Optional[bool] = None
    influencer_details: Optional[InfluencerDetailsInput] = None
    final_reply: Optional[str] = None
    next_action: Optional[NextAction] = None
    influencer_id: Optional[str] = None
    campaign_id: Optional[str] = None
