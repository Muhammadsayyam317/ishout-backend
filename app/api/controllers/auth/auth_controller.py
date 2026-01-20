from typing import Dict, Any
from app.core.exception import InternalServerErrorException, UnauthorizedException
from app.core.security.jwt import verify_token
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
