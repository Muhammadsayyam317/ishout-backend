from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from app.config import config

load_dotenv()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    """Connect to MongoDB and store client and DB globally. Safe to call multiple times."""
    global _client, _db
    if _client is not None and _db is not None:
        return
    try:
        _client = AsyncIOMotorClient(
            config.MONGODB_ATLAS_URI,
            maxPoolSize=10,
            minPoolSize=0,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            retryWrites=True,
        )
        _db = _client[config.MONGODB_ATLAS_DB_NAME]
        await _client.server_info()
        print("✅ MongoDB connected successfully")
    except Exception as e:
        _client = None
        _db = None
        raise RuntimeError(f"Error connecting to MongoDB: {e}")


async def connection_info():
    """Return MongoDB connection details."""
    if not _client:
        raise RuntimeError("MongoDB client not initialized")

    server_status = await _client.admin.command("serverStatus")
    connections = server_status.get("connections", {})

    info = {
        "connection_info": {
            "is_connected": True,
            "connection_count": connections.get("current", 0),
            "available": connections.get("available", 0),
            "total_created": connections.get("totalCreated", 0),
            "has_async_client": isinstance(_client, AsyncIOMotorClient),
            "has_db": _db is not None,
            "async_client_id": id(_client),
            "db_name": _db.name if _db is not None else None,
        },
        "mongodb_server_connections": connections.get("current", 0),
        "message": f"✅ {connections.get('current', 0)} active MongoDB connection(s)",
    }

    return info


async def close() -> None:
    """Close MongoDB connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        print("🧹 MongoDB connection closed.")
        _client = None
        _db = None
    else:
        print("❌ MongoDB client not initialized.")


def get_db() -> AsyncIOMotorDatabase:
    """Return the current MongoDB database instance."""
    if _db is None:
        raise RuntimeError("❌ MongoDB database not initialized.")
    return _db
