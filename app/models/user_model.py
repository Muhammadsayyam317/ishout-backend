from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""
    COMPANY = "company"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CompanyRegistrationRequest(BaseModel):
    """Request model for company registration"""
    company_name: str
    email: EmailStr
    password: str
    contact_person: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response model for user data"""
    user_id: str
    company_name: str
    email: str
    contact_person: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class LoginResponse(BaseModel):
    """Response model for login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChangeRequest(BaseModel):
    """Request model for password change"""
    current_password: str
    new_password: str


class UserUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class UserCampaignResponse(BaseModel):
    """Response model for user's campaigns with approved influencers"""
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
