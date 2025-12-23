from bson.objectid import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from typing import Dict, Any

from app.models.user_model import UserResponse, UserRole, UserStatus
from app.utils.helpers import convert_objectid


async def get_all_users(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = (
            await users_collection.find({"role": UserRole.COMPANY.value})
            .sort("created_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
            .to_list(length=page_size)
        )
        user = [convert_objectid(doc) for doc in user]
        user_response = [
            UserResponse(
                user_id=str(user["_id"]),
                company_name=user["company_name"],
                email=user["email"],
                contact_person=user["contact_person"],
                phone=user["phone"],
                role=UserRole(user["role"]),
                status=UserStatus(user["status"]),
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            ).model_dump()
            for user in user
        ]
        total = await users_collection.count_documents({"role": UserRole.COMPANY.value})
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        return {
            "status_code": 200,
            "message": "Users retrieved successfully",
            "users": user_response,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")


async def update_user_status(user_id: str, status: str) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")

        if status not in [
            UserStatus.ACTIVE.value,
            UserStatus.INACTIVE.value,
            UserStatus.SUSPENDED.value,
        ]:
            raise HTTPException(status_code=400, detail="Invalid status")

        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"status": status}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user = convert_objectid(updated_user)
        updated_user_response = UserResponse(
            user_id=str(updated_user["_id"]),
            company_name=updated_user["company_name"],
            email=updated_user["email"],
            contact_person=updated_user["contact_person"],
            phone=updated_user["phone"],
            role=UserRole(updated_user["role"]),
            status=UserStatus(updated_user["status"]),
        ).model_dump()
        return {
            "status_code": 200,
            "message": "User status updated successfully",
            "user": updated_user_response,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating user status: {str(e)}"
        )
