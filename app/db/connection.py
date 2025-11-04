from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from app.config import config

load_dotenv()

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    """Connect to MongoDB and store client and DB globally. Safe to call multiple times."""
    global client, db
    if client is not None and db is not None:
        return
    try:
        client = AsyncIOMotorClient(
            config.MONGODB_ATLAS_URI,
        )
        db = client[config.MONGODB_ATLAS_DB_NAME]
        await client.server_info()
        print("✅ MongoDB connected successfully")
    except Exception as e:
        client = None
        db = None
        raise RuntimeError(f"Error connecting to MongoDB: {e}")


async def close() -> None:
    """Close MongoDB connection."""
    global client, db
    if client is not None:
        client.close()
        print("🧹 MongoDB connection closed.")
        client = None
        db = None
    else:
        print("❌ MongoDB client not initialized.")


def get_db() -> AsyncIOMotorDatabase:
    """Return the current MongoDB database instance."""
    if db is None:
        raise RuntimeError("Error: MongoDB database not initialized.")
    return db
