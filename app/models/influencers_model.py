from pydantic import BaseModel
from typing import List, Optional

class FindInfluencerRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    limit: str
    country: List[str]


class DeleteInfluencerRequest(BaseModel):
    """Request model to delete influencer data and embeddings from a platform collection.

    Provide at least one identifier. If multiple are provided, they are combined with OR.
    """
    platform: str
    influencer_id: str
