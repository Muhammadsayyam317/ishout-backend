from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


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


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None


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
