from typing import TypedDict, Optional, Annotated


def take_first(a, b):
    """Generic binary reducer that takes the first non-None value.
    This prevents InvalidUpdateError when multiple nodes return state with the same field.
    LangGraph expects a binary function (a, b) -> c."""
    if a is not None:
        return a
    return b


class ConversationState(TypedDict, total=False):
    sender_id: Annotated[Optional[str], take_first]
    user_message: Annotated[Optional[str], take_first]
    intent: Optional[str]

    platform: Optional[str]
    category: Optional[str]
    country: Optional[str]
    number_of_influencers: Optional[int]

    reply: Annotated[Optional[str], take_first]
    last_active: Optional[float] = None
    event_data: dict
    campaign_id: Optional[str]
    done: Optional[bool]
    reply_sent: Optional[bool]
    thread_id: Optional[str]
