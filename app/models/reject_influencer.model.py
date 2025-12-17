from pydantic import BaseModel
from typing import List


class RegenerateInfluencerRequest(BaseModel):
    category: str
    country: str
    platform: str
    followers: int
    limit: int
    campaign_id: str
    generated_influencers: List[str]
    rejected_influencers: List[str]
