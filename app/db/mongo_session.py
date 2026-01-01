from app.config.credentials_config import config
from app.db.connection import get_db
from pymongo import ASCENDING

SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def get_session_collection():
    print("Getting session collection")
    print(f"Collection name: {config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS}")
    db = get_db()
    print(f"DB: {db}")
    session_collection = db.get_collection(
        config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS
    )
    print(f"Session collection: {session_collection}")
    session_collection.create_index(
        [("last_active", ASCENDING)],
        expireAfterSeconds=SESSION_EXPIRY_SECONDS,
    )
    return session_collection
