from pydantic import BaseModel
from typing import Optional, List


class AnalyzeMessageOutput(BaseModel):
    intent: str
    pricing_mentioned: bool
    budget_amount: Optional[float] = None
    currency: Optional[str] = None
    deliverables_mentioned: bool
    deliverables: Optional[str] = None
    timeline_mentioned: bool
    timeline: Optional[str] = None
    platforms_mentioned: bool
    platforms: Optional[List[str]] = None
    usage_rights_mentioned: bool
    exclusivity_mentioned: bool
    missing_required_details: List[str]
    recommended_next_action: str


class MessageInput(BaseModel):
    message: str
    thread_id: Optional[str] = None


class GenerateReplyOutput(BaseModel):
    reply: str


class GuardrailOutput(BaseModel):
    response: str


class OutputGuardrailResult(BaseModel):
    allowed: bool
    reason: str | None = None
    escalate: bool = False
    fallback: str | None = None
    output_info: str | None = None
    tripwire_triggered: bool | None = None


class InputGuardrailResult(BaseModel):
    allowed: bool
    reason: str | None = None
    escalate: bool = False
    fallback: str | None = None
    tripwire_triggered: bool = False


class InstagramMessage(BaseModel):
    thread_id: str
    sender_type: str
    platform: str
    username: str
    message: str
    timestamp: str
    attachments: list


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
