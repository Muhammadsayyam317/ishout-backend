from pydantic import BaseModel
from typing import Optional


class SearchRejectRegenerateInfluencersRequest(BaseModel):
    platform: Optional[str] = None
    campaign_id: str
    rejected_influencer_id: str
    limit: int = 1
