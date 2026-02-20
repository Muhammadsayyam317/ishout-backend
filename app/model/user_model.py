from typing import Optional, Dict, Any
from bson import ObjectId
from app.Schemas.user_model import UserStatus
from app.config import config
from app.db.connection import get_db


class UserModel:
    collection_name = config.MONGODB_ATLAS_COLLECTION_USERS

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

    @staticmethod
    async def update_by_email(email: str, update_data: Dict[str, Any]):
        db = get_db()
        return await db.get_collection(UserModel.collection_name).update_one(
            {"email": email},
            {"$set": update_data}
        )