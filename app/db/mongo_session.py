from app.db.connection import get_pymongo_db
from pymongo import ASCENDING

SESSION_EXPIRY_SECONDS = 600  # 10 minutes


def get_session_collection():
    """
    Lazily get the whatsapp_sessions collection.

    We call get_pymongo_db() only at runtime (after Mongo has been connected
    in the FastAPI lifespan), not at import time, to avoid
    'PyMongo database not initialized' errors.
    """
    db = get_pymongo_db()
    session_collection = db["whatsapp_sessions"]
    # Ensure TTL index exists (idempotent)
    session_collection.create_index(
        [("last_active", ASCENDING)],
        expireAfterSeconds=SESSION_EXPIRY_SECONDS,
    )
    return session_collection
