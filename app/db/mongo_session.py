from app.config.credentials_config import config
from app.db.connection import get_db
from pymongo import ASCENDING

SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def get_session_collection():
    try:
        print("Entering into session collection")
        db = get_db()
        session_collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS
        )
        print(
            f"Session collection: collection name: {config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS}"
        )
        session_collection.create_index(
            [("last_active", ASCENDING)],
            expireAfterSeconds=SESSION_EXPIRY_SECONDS,
        )
        print("Exiting from session collection")
        return session_collection
    except Exception as e:
        print(f"Error getting session collection: {e}")
        raise e
