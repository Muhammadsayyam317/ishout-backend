from typing import Optional
from pydantic import BaseModel


class HumanTakeoverRequest(BaseModel):
    enabled: bool


class HumanMessageRequest(BaseModel):
    message: str = ""
    message_type: str = "text"          # "text" | "image" | "video" | "audio" | "document"
    meta_media_id: Optional[str] = None  # from upload-media endpoint (transient)
    media_url: Optional[str] = None      # S3 URL (permanent, stored in DB)
    media_mime_type: Optional[str] = None
    media_filename: Optional[str] = None  # for documents
