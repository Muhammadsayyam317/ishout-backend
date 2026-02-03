from typing import Dict, Any
from app.core.exception import (
    UnauthorizedException,
)
from app.core.security.jwt import verify_token
from app.Schemas.user_model import UserLoginRequest
from app.services.Auth.auth_service import AuthService
from fastapi import HTTPException
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
)


async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        return await AuthService.login(request_data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=e.detail["message"])


async def register_company(
    request_data: CompanyRegistrationRequest,
) -> Dict[str, Any]:
    return await AuthService.register_company(request_data)


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
        raise HTTPException(status_code=500, detail=str(e))


# async def instagram_oauth_callback(code: str):
#     async with httpx.AsyncClient() as client:
#         token_res = await client.post(
#             "https://graph.facebook.com/v19.0/oauth/access_token",
#             data={
#                 "client_id": config.META_APP_ID,
#                 "client_secret": config.META_APP_SECRET,
#                 "redirect_uri": config.INSTAGRAM_REDIRECT_URL,
#                 "code": code,
#             },
#         )
#     return token_res.json()
