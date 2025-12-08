from typing import List, TypedDict, Optional, Annotated


def take_first(a, b):
    if a is not None:
        return a
    return b


def take_second(a, b):
    if b is not None:
        return b
    return a


def take_second_allow_none(a, b):
    return b


def merge_arrays(a, b):
    """Merge two arrays, keeping unique values."""
    if a is None:
        a = []
    if b is None:
        b = []
    if not isinstance(a, list):
        a = [a] if a else []
    if not isinstance(b, list):
        b = [b] if b else []
    result = list(a)
    for item in b:
        if item not in result:
            result.append(item)
    return result


class ConversationState(TypedDict, total=False):
    sender_id: Annotated[Optional[str], take_first]
    user_message: Annotated[Optional[str], take_second]

    intent: Annotated[Optional[str], take_first]

    platform: Annotated[Optional[List[str]], merge_arrays]
    category: Annotated[Optional[List[str]], merge_arrays]
    country: Annotated[Optional[List[str]], merge_arrays]
    followers: Annotated[Optional[List[str]], merge_arrays]

    limit: Annotated[Optional[int], take_second]

    reply: Annotated[Optional[str], take_second_allow_none]
    reply_sent: Annotated[Optional[bool], take_second]

    campaign_id: Annotated[Optional[str], take_first]
    campaign_created: Annotated[Optional[bool], take_second]
    ready_for_campaign: Annotated[Optional[bool], take_second]
    done: Annotated[Optional[bool], take_second]

    last_active: Annotated[Optional[float], take_first]
    event_data: Annotated[dict, take_first]
    thread_id: Annotated[Optional[str], take_first]

    debug_log: Annotated[Optional[list], take_first]
