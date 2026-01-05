from pydantic import BaseModel


class HumanTakeoverRequest(BaseModel):
    enabled: bool
