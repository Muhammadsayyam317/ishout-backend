from typing import Optional

from pydantic import BaseModel, constr


class Whatsapp_Users_Sessions(BaseModel):
    sender_id: str
    name: str
    last_message: str
    last_active: float
    platform: list[str]
    ready_for_campaign: bool
    campaign_created: bool
    acknowledged: bool
    conversation_round: int
    status: str


class HumanMessageRequest(BaseModel):
    message: constr(min_length=1)
    negotiation_id: Optional[str] = None


class AdminApproveVideoRequest(BaseModel):
    negotiation_id: str
    video_url: str
    # Example: "admin_approved"
    video_status: str = "admin_approved"
    # This is the WhatsApp thread id / brand phone used as `thread_id`
    brand_thread_id: str
