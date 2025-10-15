from pydantic import BaseModel
from typing import Optional

class FindInfluencerRequest(BaseModel):
    category: str
    platform: str
    followers: Optional[str] = None
    country: Optional[str] = None
    limit: Optional[int] = 10
