from typing import Optional, Dict, Any
from app.db.connection import get_db


class UserModel:
    collection_name = "users"

    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        return await db.get_collection(UserModel.collection_name).find_one(
            {"email": email}
        )

    @staticmethod
    async def create(user_doc: Dict[str, Any]):
        db = get_db()
        return await db.get_collection(UserModel.collection_name).insert_one(user_doc)
