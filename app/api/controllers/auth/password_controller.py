from datetime import datetime, timedelta, timezone
import random
from bson import ObjectId
from fastapi import BackgroundTasks
from typing import Dict, Any
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


def create_reset_password_token(email: str):
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=10)
    data = {"sub": email, "exp": expiry_time}
    token = jwt.encode(data, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
    return {
        "token": token,
        "forget_url_link": f"{config.FRONTEND_URL}/reset-password?token={token}",
        "expiry_time": expiry_time,
    }


async def forgot_password(
    background_tasks: BackgroundTasks, request_data: ForgetPasswordRequest
) -> Dict[str, Any]:
    try:
        print("Email: ", request_data.email)
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user_email = await users_collection.find_one({"email": request_data.email})
        if not user_email:
            raise EmailNotFoundException()
        if user_email["status"] != UserStatus.ACTIVE:
            raise AccountNotActiveException()
        secret_token_data = create_reset_password_token(user_email["email"])
        forget_url_link = (
            f"{config.FRONTEND_URL}/reset-password?token={secret_token_data['token']}"
        )
        expiry_time = secret_token_data["expiry_time"]
        email_body = {
            "company_name": user_email["company_name"],
            "forget_url_link": forget_url_link,
            "expiry_time": expiry_time,
        }
        otp = generate_otp(user_email["email"])
        background_tasks.add_task(
            send_reset_email, user_email["email"], email_body, otp
        )
        return {
            "message": "Password reset email sent",
            "otp": otp,
        }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


otp_storage = {}


def generate_otp(email: str):
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp
    return otp


async def verify_otp(token: str, otp: str):
    try:
        if token not in otp_storage:
            raise UnauthorizedException()
        if otp != otp_storage[token]:
            del otp_storage[token]
            raise UnauthorizedException()
        del otp_storage[token]
        return {"message": "OTP verified successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


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
