from typing import Any, Dict
from pydantic import BaseModel


class NotifyPayload(BaseModel):
    user_id: str | None = None
    title: str
    message: str
    data: Dict[str, Any] | None = None
