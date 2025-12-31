from typing import List, TypedDict, Optional, Annotated

from app.utils.helpers import (
    merge_arrays,
    take_first,
    take_second,
    take_second_allow_none,
)


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
    acknowledged: Annotated[Optional[bool], take_second]
    done: Annotated[Optional[bool], take_second]
    name: Annotated[Optional[str], take_first]
    last_active: Annotated[Optional[float], take_first]
    thread_id: Annotated[Optional[str], take_first]
    debug_log: Annotated[Optional[list], take_first]
