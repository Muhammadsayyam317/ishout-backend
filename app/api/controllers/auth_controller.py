import hashlib
import secrets
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.user_model import (
    PasswordChangeRequest,
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


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    if not config.JWT_SECRET_KEY:
        raise ValueError("JWT Secret Key is not configured in environment variables")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
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


async def change_password(
    user_id: str, request_data: PasswordChangeRequest
) -> Dict[str, Any]:
    """Change user password"""
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return HTTPException(status_code=404, detail="User not found")
        # Verify current password
        if not verify_password(request_data.current_password, user.get("password")):
            return HTTPException(
                status_code=401, detail="Current password is incorrect"
            )

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


async def get_current_user(token: str) -> Dict[str, Any]:
    try:
        payload = verify_token(token)
        if not payload:
            return HTTPException(status_code=401, detail="Invalid token")
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
