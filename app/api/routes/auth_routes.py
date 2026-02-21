from fastapi import APIRouter, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from app.Schemas.password import VerifyOtpRequest
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
    ForgetPasswordRequest,
    PasswordChangeRequest,
    UserLoginRequest,
)
from fastapi import HTTPException
from app.api.controllers.auth.auth_controller import (
    login_user,
    register_company,
)
from app.api.controllers.auth.password_controller import (
    change_password,
    forgot_password,
    verify_otp,
)
from app.core.security.jwt import verify_token
from datetime import datetime, timezone
from app.model.user_model import UserModel
from app.Schemas.user_model import UserStatus
from app.core.exception import UnauthorizedException
from app.core.exception import InternalServerErrorException

router = APIRouter()


@router.post("/register", tags=["Auth"])
async def register_route(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        return await register_company(request_data, background_tasks)
    except HTTPException:
        raise
    except Exception:
        raise InternalServerErrorException(
            message="Internal server error"
        )


@router.post("/login", tags=["Auth"])
async def login_route(request_data: UserLoginRequest):
    try:
        return await login_user(request_data)
    except HTTPException:
        raise
    except Exception:
        raise InternalServerErrorException(
            message="Internal server error"
        )



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
    return await verify_otp(request_data.email, request_data.otp)


@router.post("/change_password", tags=["Auth"])
async def change_password_route(request_data: PasswordChangeRequest):
    try:
        return await change_password(request_data)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.get("/verify-email")
async def verify_email(token: str = Query(...)):
    try:
        payload = verify_token(token)

        if not payload or payload.get("type") != "email_verification":
            return JSONResponse(
                status_code=400,
                content={"message": "Invalid or expired verification token."},
            )

        email = payload.get("email")
        user = await UserModel.find_by_email(email)
        if not user:
            return JSONResponse(
                status_code=404,
                content={"message": "User not found."},
            )

        if user["status"] == UserStatus.ACTIVE:
            return JSONResponse(
                status_code=200,
                content={"message": "Account already verified."},
            )

        # update user status
        await UserModel.update_by_email(
            email,
            {"status": UserStatus.ACTIVE, "updated_at": datetime.now(timezone.utc)},
        )

        return JSONResponse(
            status_code=200,
            content={"message": "Email verified successfully."},
        )

    except UnauthorizedException as e:
        return JSONResponse(
            status_code=401,
            content={"message": e.detail.get("message", "Unauthorized")},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": str(e) or "Something went wrong."},
        )
