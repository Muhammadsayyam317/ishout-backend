from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    """Singleton pattern for database connection"""

    _instance: "Database" = None
    _client: AsyncIOMotorClient | None = None
    _db: AsyncIOMotorDatabase | None = None
    _initialized: bool = False


@staticmethod
def connect() -> None:
    try:
        Database._client = AsyncIOMotorClient(os.getenv("MONGODB_ATLAS_URI"))
        Database._db = Database._client[os.getenv("MONGODB_ATLAS_DB_NAME")]
    except Exception as e:
        raise RuntimeError(f"Error connecting to MongoDB: {e}")


@staticmethod
def close() -> None:
    if Database._client is not None:
        Database._client.close()
    else:
        raise RuntimeError("MongoDB client not initialized. .")


def get_db() -> AsyncIOMotorDatabase:
    if Database._db is None:
        return Database._db
    else:
        raise RuntimeError("MongoDB database not initialized..")
