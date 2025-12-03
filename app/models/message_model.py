from typing import Literal
from pydantic import BaseModel


class MessageRequestType(BaseModel):
    intent: Literal["find_influencers", "other"]


class UserMessage(BaseModel):
    message: str
