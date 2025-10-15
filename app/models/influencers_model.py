from pydantic import BaseModel

class FindInfluencerRequest(BaseModel):
    category: str
    platform: str = None
    country: str = None
    limit: int= 10
    followers: str = None
