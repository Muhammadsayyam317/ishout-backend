from pydantic import BaseModel
from typing import List, Optional

class FindInfluencerRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    limit: str
    country: List[str]
    # Optional: request a new batch size overriding limit for subsequent calls
    more: Optional[int] = None
    # Optional: IDs/handles/urls already seen or accepted; ensure fresh results only
    exclude_ids: Optional[List[str]] = None


class DeleteInfluencerRequest(BaseModel):
    """Request model to delete influencer data and embeddings from a platform collection.

    Provide at least one identifier. If multiple are provided, they are combined with OR.
    """
    platform: str
    influencer_id: str


class MoreInfluencerRequest(BaseModel):
    """Request model for fetching more (fresh) influencers.

    Requires a new desired count (more) and a list of exclude_ids to avoid
    returning items the user has already seen or accepted. Filters are
    required to maintain the same search context; send the same filters as
    the initial request or adjusted ones if needed.
    """
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    more: int
    exclude_ids: List[str]
