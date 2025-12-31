from typing import Dict, Any
from app.model.user_model import UserModel
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
    UserResponse,
    UserRole,
    UserStatus,
)
from app.core.security.password import hash_password, verify_password
from app.core.security.jwt import create_access_token
from app.core.exception import UnauthorizedException
from app.services.email.email_service import (
    WELCOME_EMAIL_TEMPLATE_HTML,
    send_welcome_email,
)
from datetime import datetime, timezone
from fastapi import BackgroundTasks


class AuthService:

    @staticmethod
    async def login(request_data: UserLoginRequest) -> Dict[str, Any]:
        user = await UserModel.find_by_email(request_data.email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        if user["status"] != UserStatus.ACTIVE:
            raise UnauthorizedException("Account is not active")

        if not verify_password(request_data.password, user["password"]):
            raise UnauthorizedException("Invalid email or password")

        token_data = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
        }

        access_token = create_access_token(token_data)
        user_response = UserResponse(
            user_id=str(user["_id"]),
            company_name=user["company_name"],
            email=user["email"],
            contact_person=user["contact_person"],
            phone=user.get("phone"),
            role=user["role"],
            status=user["status"],
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    @staticmethod
    async def register_company(
        request_data: CompanyRegistrationRequest,
        background_tasks: BackgroundTasks,
    ) -> Dict[str, Any]:

        existing_user = await UserModel.find_by_email(request_data.email)
        if existing_user:
            raise UnauthorizedException("User with this email already exists")

        hashed_password = hash_password(request_data.password)
        now = datetime.now(timezone.utc)

        user_doc = request_data.model_dump(exclude={"password"}) | {
            "password": hashed_password,
            "role": UserRole.COMPANY,
            "status": UserStatus.ACTIVE,
            "created_at": now,
            "updated_at": now,
        }

        result = await UserModel.create(user_doc)
        user_id = str(result.inserted_id)

        token_data = {
            "user_id": user_id,
            "email": request_data.email,
            "role": UserRole.COMPANY,
        }

        access_token = create_access_token(token_data)

        user_response = UserResponse(
            user_id=user_id,
            company_name=request_data.company_name,
            email=request_data.email,
            contact_person=request_data.contact_person,
            phone=request_data.phone,
            role=UserRole.COMPANY,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

        background_tasks.add_task(
            send_welcome_email,
            [request_data.email],
            "Welcome to Ishout",
            WELCOME_EMAIL_TEMPLATE_HTML,
        )

        return {
            "message": "Company registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }
