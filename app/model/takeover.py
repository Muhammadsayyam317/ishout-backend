from typing import Optional

from pydantic import BaseModel


class HumanTakeoverRequest(BaseModel):
    enabled: bool


class NegotiationApprovalRequest(BaseModel):
    # Optional: provide only one field at a time.
    # Values are stored as strings (or null to clear).
    admin_approved: Optional[str] = None
    Brand_approved: Optional[str] = None
