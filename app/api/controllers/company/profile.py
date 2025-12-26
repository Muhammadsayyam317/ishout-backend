from datetime import datetime, timezone
from typing import Any, Dict
from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from app.Schemas.user_model import UserResponse, UserUpdateRequest


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "status_code": 200,
            "message": "Profile retrieved successfully",
            "user": UserResponse(
                user_id=str(user["_id"]),
                company_name=user.get("company_name"),
                email=user.get("email"),
                contact_person=user.get("contact_person"),
                phone=user.get("phone"),
                role=user.get("role"),
                status=user.get("status"),
            ).model_dump(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving profile: {str(e)}"
        )


async def update_user_profile(
    user_id: str, request_data: UserUpdateRequest
) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        update_data = request_data.model_dump()
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")

        return {
            "status_code": 200,
            "message": "Profile updated successfully",
            "user": UserUpdateRequest(
                company_name=user.get("company_name"),
                email=user.get("email"),
                contact_person=user.get("contact_person"),
                phone=user.get("phone"),
            ).model_dump(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")
