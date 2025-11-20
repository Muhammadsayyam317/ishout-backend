from fastapi import HTTPException
from app.db.connection import get_db
from bson import ObjectId


async def company_data(user_id: str):
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": str(user["_id"]),
            "phone": user["phone"],
            "company_name": user["company_name"],
            "contact_person": user["contact_person"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
