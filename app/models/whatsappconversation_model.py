from typing import TypedDict, Optional, Annotated


def take_first(a, b):
    if a is not None:
        return a
    return b


def take_second(a, b):
    if b is not None:
        return b
    return a


class ConversationState(TypedDict, total=False):
    sender_id: Annotated[Optional[str], take_first]
    user_message: Annotated[Optional[str], take_second]
    intent: Annotated[Optional[str], take_first]

    platform: Annotated[Optional[str], take_second]
    category: Annotated[Optional[str], take_second]
    country: Annotated[Optional[str], take_second]
    number_of_influencers: Annotated[Optional[int], take_second]

    reply: Annotated[Optional[str], take_second]
    last_active: Annotated[Optional[float], take_first]
    event_data: Annotated[dict, take_first]
    campaign_id: Annotated[Optional[str], take_first]
    done: Annotated[Optional[bool], take_first]
    reply_sent: Annotated[Optional[bool], take_first]
    thread_id: Annotated[Optional[str], take_first]
    debug_log: Annotated[Optional[list], take_first]
