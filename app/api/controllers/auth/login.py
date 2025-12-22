from typing import Any, Dict
from fastapi import HTTPException
from app.api.controllers.auth_controller import create_access_token, verify_password
from app.db.connection import get_db
from app.models.user_model import UserLoginRequest, UserResponse, UserStatus


async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"email": request_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if user["status"] != UserStatus.ACTIVE:
            raise HTTPException(status_code=401, detail="Account is not active")
        if not verify_password(request_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
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
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response.model_dump(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
