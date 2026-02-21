from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.utils.helpers import normalize_phone


class UserRole(str, Enum):
    COMPANY = "company"
    ADMIN = "admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CompanyRegistrationRequest(BaseModel):
    contact_person: str
    company_name: str
    email: EmailStr
    password: str
    phone: str

# ---- contact_person ----
    @field_validator("contact_person")
    @classmethod
    def validate_contact_person(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Contact person is required")
        return value.strip()

    # ---- company_name ----
    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Company name is required")
        return value.strip()

    # ---- password ----
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value

    # ---- phone ----
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Phone number is required")

        normalized = normalize_phone(value)

        if not normalized:
            raise ValueError("Invalid phone number")

        return normalized


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    company_name: str
    email: EmailStr
    contact_person: str
    phone: str
    role: UserRole
    status: UserStatus
    

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgetPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None  

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Phone number is required")

        normalized = normalize_phone(value)

        if not normalized:
            raise ValueError("Invalid phone number")

        return normalized



class UserCampaignResponse(BaseModel):
    campaign_id: str
    name: str
    description: Optional[str] = None
    platform: List[str]
    category: List[str]
    followers: List[str]
    country: List[str]
    approved_influencers: List[dict] = []
    total_approved: int = 0
    created_at: datetime
    updated_at: datetime


class UserSchema(BaseModel):
    phone: str

    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        if not value:
            raise ValueError("Phone number is required")
        phone = normalize_phone(value)
        if not phone:
            raise ValueError("Invalid phone number")
        return phone
