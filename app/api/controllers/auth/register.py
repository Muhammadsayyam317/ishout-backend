from typing import Dict, Any
from datetime import datetime, timezone
from app.api.controllers.auth_controller import create_access_token, hash_password
from app.db.connection import get_db
from app.models.user_model import (
    CompanyRegistrationRequest,
    UserResponse,
    UserRole,
    UserStatus,
)

from fastapi import HTTPException

# from app.services.email_service import WELCOME_EMAIL_TEMPLATE_HTML, send_welcome_email


async def register_company(request_data: CompanyRegistrationRequest) -> Dict[str, Any]:
    # backgroundtask.add_task(
    #     send_welcome_email,
    #     [request_data.email],
    #     "Welcome to Ishout",
    #     WELCOME_EMAIL_TEMPLATE_HTML,
    # )
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        existing_user = await users_collection.find_one({"email": request_data.email})
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )
        hashed_password = hash_password(request_data.password)
        now = datetime.now(timezone.utc)
        user_doc = request_data.model_dump(exclude={"password"}) | {
            "password": hashed_password,
            "role": UserRole.COMPANY,
            "status": UserStatus.ACTIVE,
            "created_at": now,
            "updated_at": now,
        }
        result = await users_collection.insert_one(user_doc)
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

        return {
            "message": "Company registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
