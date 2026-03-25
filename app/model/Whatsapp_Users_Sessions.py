from typing import Optional
from pydantic import BaseModel


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
    message: str = ""                     # text body or caption
    message_type: str = "text"            # "text" | "image" | "video" | "audio" | "document"
    meta_media_id: Optional[str] = None   # from POST /upload-media (transient, for sending)
    media_url: Optional[str] = None       # S3 URL (permanent, stored in DB)
    media_mime_type: Optional[str] = None
    media_filename: Optional[str] = None  # for document type
