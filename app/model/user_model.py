from typing import Optional, Dict, Any

from bson import ObjectId
from pydantic import field_validator
from app.Schemas.user_model import UserStatus
from app.db.connection import get_db
from app.utils.helpers import normalize_phone


class UserModel:
    collection_name = "users"

    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        return await db.get_collection(UserModel.collection_name).find_one(
            {"email": email}
        )

    @staticmethod
    async def find_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        return await db.get_collection(UserModel.collection_name).find_one(
            {"phone": phone}
        )

    @staticmethod
    async def find_by_status(status: UserStatus) -> Optional[Dict[str, Any]]:
        db = get_db()
        return await db.get_collection(UserModel.collection_name).find_many(
            {"status": status}
        )

    @staticmethod
    async def create(user_doc: Dict[str, Any]):
        db = get_db()
        return await db.get_collection(UserModel.collection_name).insert_one(user_doc)

    @staticmethod
    async def update_status(user_id: str, status: UserStatus):
        db = get_db()
        return await db.get_collection(UserModel.collection_name).update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"status": status}}
        )

    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        if not value:
            raise ValueError("Phone number is required")
        phone = normalize_phone(value)
        if not phone:
            raise ValueError("Invalid phone number")
        return phone
