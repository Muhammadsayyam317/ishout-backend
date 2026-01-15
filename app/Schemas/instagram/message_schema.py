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
    final_reply: str
