from typing import TypedDict, Optional, Annotated


def take_first(values):
    """Reducer that takes the first non-None value from a list of values."""
    for value in values:
        if value is not None:
            return value
    return None


class ConversationState(TypedDict, total=False):
    sender_id: Annotated[Optional[str], take_first]
    user_message: Optional[str]
    intent: Optional[str]

    platform: Optional[str]
    category: Optional[str]
    country: Optional[str]
    number_of_influencers: Optional[int]

    reply: Optional[str]
    last_active: Optional[float] = None
    event_data: dict
