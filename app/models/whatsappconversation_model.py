from typing import TypedDict, Optional, Annotated


def take_first_sender_id(a, b):
    """Binary reducer that takes the first non-None value for sender_id.
    This prevents InvalidUpdateError when multiple nodes return state with sender_id.
    LangGraph expects a binary function (a, b) -> c."""
    if a is not None:
        return a
    return b


class ConversationState(TypedDict, total=False):
    sender_id: Annotated[Optional[str], take_first_sender_id]
    user_message: Optional[str]
    intent: Optional[str]

    platform: Optional[str]
    category: Optional[str]
    country: Optional[str]
    number_of_influencers: Optional[int]

    reply: Optional[str]
    last_active: Optional[float] = None
    event_data: dict
    campaign_id: Optional[str]
    done: Optional[bool]
    reply_sent: Optional[bool]
    thread_id: Optional[str]
