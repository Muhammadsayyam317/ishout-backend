from app.config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from pymongo.results import InsertOneResult


class InstagramMessageModel:
    collection_name = config.INSTAGRAM_MESSAGE_COLLECTION

    @staticmethod
    async def create(payload: dict) -> InsertOneResult:
        try:
            db = get_db()
            collection = db.get_collection(InstagramMessageModel.collection_name)
            return await collection.insert_one(payload)
        except Exception as e:
            raise InternalServerErrorException(message=str(e))
