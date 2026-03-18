from datetime import datetime, timezone
from typing import Any, Dict
from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from app.Schemas.user_model import UserResponse, UserUpdateRequest,ChangePasswordRequest
from app.core.security.password import hash_password,verify_password
from app.config.credentials_config import config
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
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

    db = get_db()
    users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = request_data.model_dump(exclude_none=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made")

    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})

    return {
        "status_code": 200,
        "message": "Profile updated successfully",
        "user": {
            "company_name": updated_user.get("company_name"),
            "email": updated_user.get("email"),
            "contact_person": updated_user.get("contact_person"),
            "phone": updated_user.get("phone"),
        },
    }

async def change_user_password(
    user_id: str,
    request_data: ChangePasswordRequest
) -> Dict[str, Any]:

    db = get_db()
    users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(request_data.old_password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    if len(request_data.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long"
        )

    hashed_password = hash_password(request_data.new_password)

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "password": hashed_password,
                "updated_at": datetime.now(timezone.utc),
            }
        }
    )

    return {
        "status_code": 200,
        "message": "Password updated successfully",
    }