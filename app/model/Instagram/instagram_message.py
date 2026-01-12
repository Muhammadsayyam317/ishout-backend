from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


class InstagramMessageModel:
    collection_name = "instagram_messages"

    @staticmethod
    async def create(payload: dict) -> dict:
        try:
            db = get_db()
            collection = db.get_collection(InstagramMessageModel.collection_name)
            await collection.insert_one(payload)
        except Exception as e:
            raise InternalServerErrorException(message=str(e))
        return payload
