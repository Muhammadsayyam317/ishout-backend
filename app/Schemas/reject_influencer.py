from pydantic import BaseModel
from typing import List, Optional


class SearchRejectRegenerateInfluencersRequest(BaseModel):
    platform: str
    category: str
    followers: List[str]
    country: List[str]
    limit: int = 1
    campaign_id: Optional[str] = None
    generated_influencers_id: Optional[List[str]] = []
    rejected_influencers_id: Optional[List[str]] = []
