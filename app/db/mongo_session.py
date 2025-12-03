from app.db.connection import get_db, get_pymongo_db
from pymongo import ASCENDING

SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def get_session_collection():
    db = get_db()
    session_collection = db.get_collection("whatsapp_sessions")
    session_collection.create_index(
        [("last_active", ASCENDING)],
        expireAfterSeconds=SESSION_EXPIRY_SECONDS,
    )
    return session_collection
