from fastapi import APIRouter, BackgroundTasks
from app.Schemas.password import VerifyOtpRequest
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
    ForgetPasswordRequest,
    PasswordChangeRequest,
    UserLoginRequest,
)

from app.api.controllers.auth.auth_controller import (
    login_user,
    register_company,
)
from app.api.controllers.auth.password_controller import (
    change_password,
    forgot_password,
    verify_otp,
)
from app.core.exception import InternalServerErrorException

router = APIRouter()


@router.post("/register", tags=["Auth"])
async def register_route(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        return await register_company(request_data, background_tasks)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.post("/login", tags=["Auth"])
async def login_route(request_data: UserLoginRequest):
    try:
        return await login_user(request_data)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.post("/forgot-password", tags=["Auth"])
async def forgot_password_route(
    background_tasks: BackgroundTasks, request_data: ForgetPasswordRequest
):
    try:
        return await forgot_password(background_tasks, request_data)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.post("/verify-otp", tags=["Auth"])
async def verify_otp_route(request_data: VerifyOtpRequest):
    try:
        return await verify_otp(request_data.email, request_data.otp)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.post("/change_password", tags=["Auth"])
async def change_password_route(request_data: PasswordChangeRequest):
    try:
        return await change_password(request_data)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e
