from datetime import datetime, timezone
from typing import Dict, Any
from bson import ObjectId
from app.Schemas.user_model import (
    PasswordChangeRequest,
)
from app.core.exception import (
    InternalServerErrorException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security.jwt import verify_token
from app.core.security.password import hash_password, verify_password
from app.db.connection import get_db
from app.Schemas.user_model import UserLoginRequest
from app.services.Auth.auth_service import AuthService
from fastapi import BackgroundTasks
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
)


async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        return await AuthService.login(request_data)
    except Exception as e:
        raise InternalServerErrorException() from e


async def register_company(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    return await AuthService.register_company(request_data, background_tasks)


async def change_password(
    user_id: str, request_data: PasswordChangeRequest
) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise NotFoundException(message="User not found")
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


async def get_current_user(token: str) -> Dict[str, Any]:
    try:
        payload = verify_token(token)
        if not payload:
            raise UnauthorizedException(message="Invalid token")
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except Exception as e:
        raise InternalServerErrorException(message=str(e))
