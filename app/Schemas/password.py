from pydantic import BaseModel, EmailStr


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


class ResetPasswordSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str
    token: str
