from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv
from app.config import config

load_dotenv()

client: AsyncIOMotorClient = None
db = None

pymongo_client: MongoClient = None
pymongo_db = None


async def connect():
    global client, db, pymongo_client, pymongo_db
    if client and db:
        return

    try:
        # Motor client for async operations
        client = AsyncIOMotorClient(
            config.MONGODB_ATLAS_URI,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
        )
        db = client[config.MONGODB_ATLAS_DB_NAME]
        # PyMongo client for langchain vector search (synchronous)
        pymongo_client = MongoClient(
            config.MONGODB_ATLAS_URI,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        pymongo_db = pymongo_client[config.MONGODB_ATLAS_DB_NAME]

    except Exception as e:
        client = None
        db = None
        pymongo_client = None
        pymongo_db = None
        raise RuntimeError(f"Error connecting to MongoDB: {e}")


async def close():
    global client, db, pymongo_client, pymongo_db

    if client:
        client.close()
        client = None
        db = None

    if pymongo_client:
        pymongo_client.close()
        pymongo_client = None
        pymongo_db = None
    else:
        print("MongoDB client not initialized.")


def get_db():
    if db is None:
        raise RuntimeError("Error: MongoDB database not initialized.")
    return db


def get_pymongo_db():
    if pymongo_db is None:
        raise RuntimeError("Error: PyMongo database not initialized.")
    return pymongo_db
