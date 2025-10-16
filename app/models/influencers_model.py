from pydantic import BaseModel
from typing import List

class FindInfluencerRequest(BaseModel):
    platform: List[str]
    category: List[str]
    followers: List[str]
    limit: str
    country: List[str]
