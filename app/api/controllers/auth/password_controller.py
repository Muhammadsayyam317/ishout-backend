from datetime import datetime, timedelta, timezone
import random
from bson import ObjectId
from fastapi import BackgroundTasks
from typing import Dict, Any
from app.agents.Whatsapp.nodes.state import redis_client
from app.core.exception import (
    AccountNotActiveException,
    EmailNotFoundException,
    InternalServerErrorException,
    UnauthorizedException,
    UserNotFoundException,
)
from app.core.security.password import hash_password, verify_password
from app.db.connection import get_db
from app.config.credentials_config import config
from app.Schemas.user_model import (
    ForgetPasswordRequest,
    PasswordChangeRequest,
    UserStatus,
)
from app.services.email.reset_email import send_reset_email
import jwt
from fastapi import HTTPException, status


def create_reset_password_token(email: str):
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)
    data = {"sub": email, "exp": expiry_time}
    token = jwt.encode(data, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
    return token


def decode_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
        email: str = payload.get("sub")
        return email
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def forgot_password(
    background_tasks: BackgroundTasks,
    request: ForgetPasswordRequest,
):
    db = get_db()
    users = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
    user = await users.find_one({"email": request.email})
    if not user:
        raise EmailNotFoundException()
    if user["status"] != UserStatus.ACTIVE:
        raise AccountNotActiveException()
    otp = generate_otp()
    otp_key = f"reset_otp:{request.email}"
    verified_key = f"reset_otp_verified:{request.email}"
    await redis_client.delete(otp_key, verified_key)
    await redis_client.setex(otp_key, 300, otp)
    background_tasks.add_task(
        send_reset_email,
        request.email,
        otp,
    )

    return {"message": "OTP sent to email"}


otp_storage = {}


def generate_otp():
    otp = str(random.randint(100000, 999999))
    return otp


async def verify_otp(email: str, otp: str):
    otp_key = f"reset_otp:{email}"
    verified_key = f"reset_otp_verified:{email}"
    stored_otp = await redis_client.get(otp_key)
    if not stored_otp or stored_otp != otp:
        raise UnauthorizedException("Invalid or expired OTP")
    if await redis_client.get(verified_key):
        raise UnauthorizedException("OTP already verified")
    await redis_client.setex(verified_key, 600, "1")
    await redis_client.delete(otp_key)
    reset_token = create_reset_password_token(email)
    return reset_token


async def change_password(
    user_id: str, request_data: PasswordChangeRequest
) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise UserNotFoundException()
        if not verify_password(request_data.current_password, user.get("password")):
            raise UnauthorizedException(message="Current password is incorrect")
        info = decode_reset_password_token(token=request_data.secret_token)
        if info is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Password Reset Payload or Reset Link Expired",
            )
        if request_data.new_password != request_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="New password and confirm password are not same.",
            )
        if not info:
            raise UnauthorizedException(message="Invalid token")
        if info != user["email"]:
            raise UnauthorizedException(message="User not found")
        new_hashed_password = hash_password(request_data.new_password)
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
            raise InternalServerErrorException(message="Failed to update password")
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def reset_password(
    email: str, otp: str, new_password: str, confirm_password: str, token: str
):
    if new_password != confirm_password:
        raise HTTPException(400, "Passwords do not match")

    # Check OTP
    otp_key = f"reset_otp:{email}"
    stored_otp = await redis_client.get(otp_key)
    if not stored_otp or stored_otp != otp:
        raise UnauthorizedException("Invalid or expired OTP")

    # Check token
    decoded_email = decode_reset_password_token(token)
    if decoded_email != email:
        raise UnauthorizedException("Invalid or expired token")

    # Update password
    db = get_db()
    users = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
    await users.update_one(
        {"email": email},
        {
            "$set": {
                "password": hash_password(new_password),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    # Delete OTP after use
    await redis_client.delete(otp_key)
    return {"message": "Password reset successful"}
