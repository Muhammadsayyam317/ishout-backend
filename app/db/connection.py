from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
from app.config import config

load_dotenv()

client: AsyncIOMotorClient = None
db = None

# PyMongo client for langchain vector search (synchronous)
pymongo_client: MongoClient = None
pymongo_db = None


async def connect():
    """Connect to MongoDB asynchronously and store globally."""
    global client, db, pymongo_client, pymongo_db
    if client and db:
        print("⚙️ MongoDB already connected.")
        return

    try:
        # Motor client for async operations
        client = AsyncIOMotorClient(config.MONGODB_ATLAS_URI)
        db = client[config.MONGODB_ATLAS_DB_NAME]

        # PyMongo client for langchain vector search (synchronous)
        pymongo_client = MongoClient(config.MONGODB_ATLAS_URI)
        pymongo_db = pymongo_client[config.MONGODB_ATLAS_DB_NAME]

        print("✅ MongoDB connected successfully (Motor + PyMongo)")
    except Exception as e:
        client = None
        db = None
        pymongo_client = None
        pymongo_db = None
        raise RuntimeError(f"Error connecting to MongoDB: {e}")


async def close():
    """Close MongoDB connection."""
    global client, db, pymongo_client, pymongo_db
    if client:
        client.close()
        client = None
        db = None
    if pymongo_client:
        pymongo_client.close()
        pymongo_client = None
        pymongo_db = None
        print("🧹 MongoDB connection closed.")
    else:
        print("❌ MongoDB client not initialized.")


def get_db():
    """Return the current MongoDB database instance (Motor - async)."""
    if db is None:
        raise RuntimeError("Error: MongoDB database not initialized.")
    return db


def get_pymongo_db():
    """Return the PyMongo database instance for langchain vector search (synchronous)."""
    if pymongo_db is None:
        raise RuntimeError("Error: PyMongo database not initialized.")
    return pymongo_db
