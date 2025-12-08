from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WhatsappUser(BaseModel):
    sender_id: str
    name: Optional[str] = None
    location: Optional[str] = None

    campaign_count: int = 0
    last_campaign_id: Optional[str] = None
    campaign_ids: List[str] = []

    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    total_messages: int = 0

    is_blocked: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
