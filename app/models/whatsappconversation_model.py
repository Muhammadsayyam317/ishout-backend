from typing import TypedDict, Optional


class ConversationState(TypedDict, total=False):
    sender_id: Optional[str]
    user_message: Optional[str]
    intent: Optional[str]

    platform: Optional[str]
    category: Optional[str]
    country: Optional[str]
    number_of_influencers: Optional[int]

    reply: Optional[str]
    last_active: Optional[float] = None
    event_data: dict
