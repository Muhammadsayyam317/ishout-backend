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
