from typing import Dict, Any
from fastapi import BackgroundTasks, HTTPException, Query
from fastapi.responses import JSONResponse
from app.Schemas.user_model import UserLoginRequest, CompanyRegistrationRequest
from app.services.Auth.auth_service import AuthService
from app.services.email.email_verification import send_verification_email
from app.core.security.jwt import create_email_verification_token, verify_token
from app.core.exception import UnauthorizedException
from datetime import datetime, timezone
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        return await AuthService.login(request_data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=e.detail["message"])

async def register_company(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:

    response = await AuthService.register_company(request_data)
    verification_token = create_email_verification_token({
        "email": request_data.email
    })

    # Add task to send email with correct token link
    background_tasks.add_task(
        send_verification_email,
        [request_data.email],
        "Verify your Ishout account",
        request_data.company_name,
        verification_token,  # pass only token
    )

    return response

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