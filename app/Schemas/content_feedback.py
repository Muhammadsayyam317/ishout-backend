from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, constr


class ContentFeedbackUpsertRequest(BaseModel):
    negotiation_id: constr(min_length=1)
    campaign_id: constr(min_length=1)
    content_url: constr(min_length=1)
    msg: constr(min_length=1)
    review_side: Literal["admin_review", "brand_review"]


class ReviewBlock(BaseModel):
    content_url: Optional[str] = None
    message: List[str] = Field(default_factory=list)


class ContentFeedbackDocument(BaseModel):
    feedback_id: str
    negotiation_id: str
    campaign_id: str
    content_url: str
    admin_Rewiew: ReviewBlock
    brand_review: ReviewBlock
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
