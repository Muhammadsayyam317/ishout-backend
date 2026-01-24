from pydantic import BaseModel


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str
