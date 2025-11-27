from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class MessageRequestType(BaseModel):
    request_type: Literal["find_influencers"] = Field(
        description="Type of message requested by the user"
    )
    confidence_score: float = Field(
        description="Confidence score of the find influencers request, ranging from 0 to 1."
    )
    description: str = Field(
        description="A cleaned and structured description of the find influencers request."
    )


class SearchDBRequest(BaseModel):
    """Represents the request structure for searching Qdrant."""

    user_input: str = Field(description="The user's question find influencers.")
    collection_name: str = Field(description="The collection to search in.")
    confidence_score: float = Field(
        description="Confidence score for search request, ranging from 0 to 1."
    )
    model_config = ConfigDict(extra="forbid")


# Define request model
class UserMessage(BaseModel):
    message: str
