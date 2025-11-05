import hashlib
import secrets
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
    UserResponse,
    UserRole,
    UserStatus,
    PasswordChangeRequest,
    UserUpdateRequest,
)
from app.db.connection import get_db
from app.config import config


# Removed eager DB retrieval to avoid initialization at import time


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
        raise HTTPException(status_code=401, detail="Invalid password")


def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    if not config.JWT_SECRET_KEY:
        raise ValueError("JWT Secret Key is not configured in environment variables")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
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
        payload = jwt.decode(
            token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile by ID"""
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=500, detail=str(e))


async def update_user_profile(
    user_id: str, request_data: UserUpdateRequest
) -> Dict[str, Any]:
    """Update user profile"""
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
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
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )

        if result.modified_count == 0:
            return {"error": "No changes made"}

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def change_password(
    user_id: str, request_data: PasswordChangeRequest
) -> Dict[str, Any]:
    """Change user password"""
    try:
        db = get_db()
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
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update password")

        return {"message": "Password changed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _get_campaign_lightweight(campaign_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        campaign["_id"] = str(campaign["_id"])

        return {
            "campaign": campaign,
            "influencers": [],
            "rejected_influencers": [],
            "total_found": len(campaign.get("influencer_ids", [])),
            "total_rejected": len(campaign.get("rejected_ids", [])),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_user_campaigns(
    user_id: str, status: Optional[str] = None
) -> Dict[str, Any]:
    try:
        db = get_db()
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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
