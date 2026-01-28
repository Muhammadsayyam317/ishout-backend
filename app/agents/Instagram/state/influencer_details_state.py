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


class InstagramConversationState(TypedDict, total=False):
    thread_id: str
    campaign_id: str
    influencer_id: str

    user_message: str
    history: list[dict]

    intent: str
    analysis: dict

    influencerResponse: dict
    pricingRules: dict

    negotiationStatus: str
    next_action: str
    final_reply: str
