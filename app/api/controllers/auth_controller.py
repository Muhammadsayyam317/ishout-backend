import hashlib
import secrets
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
    LoginResponse,
    UserResponse,
    UserRole,
    UserStatus,
    PasswordChangeRequest,
    UserUpdateRequest,
    UserCampaignResponse,
)
from app.services.embedding_service import connect_to_mongodb, sync_db
from app.api.controllers.campaign_controller import get_campaign_by_id
from app.db.connection import get_db
from app.config import config

# JWT Configuration
SECRET_KEY = (
    "your-secret-key-change-in-production"  # In production, use environment variable
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

db = get_db()


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    if not config.JWT_SECRET_KEY:
        raise ValueError("JWT Secret Key is not configured in environment variables")
    to_encode = data.copy()
    expire = datetime.now(datetime.UTC) + timedelta(
        minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        if not config.JWT_SECRET_KEY:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


async def register_company(request_data: CompanyRegistrationRequest) -> Dict[str, Any]:
    try:
        users_collection = db.get_collection("users")
        existing_user = await users_collection.find_one({"email": request_data.email})
        if existing_user:
            return {"error": "User with this email already exists"}
        # Hash password
        hashed_password = hash_password(request_data.password)

        # Create user document
        user_doc = {
            "company_name": request_data.company_name,
            "email": request_data.email,
            "password": hashed_password,
            "contact_person": request_data.contact_person,
            "phone": request_data.phone,
            "industry": request_data.industry,
            "company_size": request_data.company_size,
            "role": UserRole.COMPANY,
            "status": UserStatus.ACTIVE,
            "created_at": datetime.now(datetime.UTC),
            "updated_at": datetime.now(datetime.UTC),
        }

        # Insert user
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)

        # Create access token
        token_data = {
            "user_id": user_id,
            "email": request_data.email,
            "role": UserRole.COMPANY,
        }
        access_token = create_access_token(token_data)

        # Prepare user response
        user_response = UserResponse(
            user_id=user_id,
            company_name=request_data.company_name,
            email=request_data.email,
            contact_person=request_data.contact_person,
            phone=request_data.phone,
            industry=request_data.industry,
            company_size=request_data.company_size,
            role=UserRole.COMPANY,
            status=UserStatus.ACTIVE,
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"],
        )

        return {
            "message": "Company registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    except Exception as e:
        print(f"Error in register_company: {str(e)}")
        return {"error": str(e)}


async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"email": request_data.email})
        if not user:
            return {"error": "Invalid email or password"}
        if user["status"] != UserStatus.ACTIVE:
            return {"error": "Account is not active"}
        if not verify_password(request_data.password, user["password"]):
            return {"error": "Invalid email or password"}
        # Create access token
        token_data = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
        }
        access_token = create_access_token(token_data)

        # Prepare user response
        user_response = UserResponse(
            user_id=str(user["_id"]),
            company_name=user["company_name"],
            email=user["email"],
            contact_person=user["contact_person"],
            phone=user.get("phone"),
            industry=user.get("industry"),
            company_size=user.get("company_size"),
            role=user["role"],
            status=user["status"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    except Exception as e:
        print(f"Error in login_user: {str(e)}")
        return {"error": str(e)}


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile by ID"""
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"error": "User not found"}

        user_response = UserResponse(
            user_id=str(user["_id"]),
            company_name=user["company_name"],
            email=user["email"],
            contact_person=user["contact_person"],
            phone=user.get("phone"),
            industry=user.get("industry"),
            company_size=user.get("company_size"),
            role=user["role"],
            status=user["status"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

        return {"user": user_response.model_dump()}

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        return {"error": str(e)}


async def update_user_profile(
    user_id: str, request_data: UserUpdateRequest
) -> Dict[str, Any]:
    """Update user profile"""
    try:
        users_collection = db.collection("users")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"error": "User not found"}
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        if request_data.company_name is not None:
            update_data["company_name"] = request_data.company_name
        if request_data.contact_person is not None:
            update_data["contact_person"] = request_data.contact_person
        if request_data.phone is not None:
            update_data["phone"] = request_data.phone
        if request_data.industry is not None:
            update_data["industry"] = request_data.industry
        if request_data.company_size is not None:
            update_data["company_size"] = request_data.company_size

        # Update user
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            return {"error": "No changes made"}

        return {"message": "Profile updated successfully"}

    except Exception as e:
        print(f"Error in update_user_profile: {str(e)}")
        return {"error": str(e)}


async def change_password(
    user_id: str, request_data: PasswordChangeRequest
) -> Dict[str, Any]:
    """Change user password"""
    try:
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"error": "User not found"}
        # Verify current password
        if not verify_password(request_data.current_password, user.get("password")):
            return {"error": "Current password is incorrect"}

        # Hash new password
        new_hashed_password = hash_password(request_data.new_password)

        # Update password
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password": new_hashed_password,
                    "updated_at": datetime.now(datetime.UTC),
                }
            },
        )

        if result.modified_count == 0:
            return {"error": "Failed to update password"}

        return {"message": "Password changed successfully"}

    except Exception as e:
        print(f"Error in change_password: {str(e)}")
        return {"error": str(e)}


async def _get_campaign_lightweight(campaign_id: str) -> Dict[str, Any]:
    try:

        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return {"error": "Campaign not found"}

        campaign["_id"] = str(campaign["_id"])

        return {
            "campaign": campaign,
            "influencers": [],
            "rejected_influencers": [],
            "total_found": len(campaign.get("influencer_ids", [])),
            "total_rejected": len(campaign.get("rejected_ids", [])),
        }

    except Exception as e:
        print(f"Error in _get_campaign_lightweight: {str(e)}")
        return {"error": str(e)}


async def get_user_campaigns(
    user_id: str, status: Optional[str] = None
) -> Dict[str, Any]:
    try:
        campaigns_collection = db.get_collection("campaigns")
        query = {"user_id": user_id}
        if status:
            query["status"] = status if isinstance(status, str) else str(status)
        campaigns = (
            await campaigns_collection.find(query).sort("created_at", -1).to_list(None)
        )

        user_campaigns = []
        for campaign in campaigns:
            approved_count = len(campaign.get("influencer_ids", []))
            rejected_count = len(campaign.get("rejected_ids", []))
            generated_count = len(campaign.get("generated_influencers", []))

            campaign_dict = {
                "campaign_id": str(campaign["_id"]),
                "name": campaign["name"],
                "description": campaign.get("description"),
                "platform": campaign["platform"],
                "category": campaign["category"],
                "followers": campaign["followers"],
                "country": campaign["country"],
                "total_approved": approved_count,
                "total_rejected": rejected_count,
                "total_generated": generated_count,
                "status": campaign.get("status", "pending"),
                "status_message": _get_status_message(
                    campaign.get("status", "pending")
                ),
                "created_at": campaign["created_at"],
                "updated_at": campaign["updated_at"],
            }

            user_campaigns.append(campaign_dict)

        return {"campaigns": user_campaigns, "total": len(user_campaigns)}

    except Exception as e:
        print(f"Error in get_user_campaigns: {str(e)}")
        return {"error": str(e)}


def _get_status_message(status: str) -> str:
    status_messages = {
        "pending": "Campaign created and waiting for admin to generate influencers",
        "processing": "Admin is currently generating influencers for your campaign",
        "completed": "Campaign completed with approved influencers",
    }
    return status_messages.get(status, "Unknown status")


async def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = verify_token(token)
        if not payload:
            return None
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        return None
