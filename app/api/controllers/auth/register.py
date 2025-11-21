from typing import Dict, Any
from app.api.controllers.auth_controller import create_access_token, hash_password
from app.db.connection import get_db
from app.models.user_model import (
    CompanyRegistrationRequest,
    UserResponse,
    UserRole,
)
from fastapi import HTTPException


async def register_company(request_data: CompanyRegistrationRequest) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        existing_user = await users_collection.find_one({"email": request_data.email})
        if existing_user:
            return HTTPException(
                status_code=400, detail="User with this email already exists"
            )
        hashed_password = hash_password(request_data.password)
        user = await users_collection.insert_one(
            request_data.model_dump(exclude={"password"})
            | {"password": hashed_password}
        )
        user_id = str(user.inserted_id)
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
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

        return {
            "message": "Company registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
