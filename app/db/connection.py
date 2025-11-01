from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase
from app.config import config


class Database:
    _client: AsyncIOMotorClient | None = None
    _sync_client: MongoClient | None = None
    _db: AsyncIOMotorDatabase | None = None
    _sync_db: PyMongoDatabase | None = None
    _connection_count: int = 0  # Track connection attempts
    _is_connected: bool = False  # Track connection status

    @staticmethod
    def connect() -> None:
        """Connect to MongoDB using environment variables"""
        # Prevent multiple connections - singleton pattern
        if Database._is_connected and Database._client is not None:
            return
        
        try:
            Database._connection_count += 1
            
            # Get MongoDB URI and DB name from centralized config
            mongo_uri = config.MONGODB_ATLAS_URI
            db_name = config.MONGODB_ATLAS_DB_NAME
            
            # Create async and sync clients
            Database._client = AsyncIOMotorClient(mongo_uri)
            Database._sync_client = MongoClient(mongo_uri)
            
            # Get database instances
            Database._db = Database._client[db_name]
            Database._sync_db = Database._sync_client[db_name]
            
            Database._is_connected = True
            
        except Exception as e:
            Database._is_connected = False
            raise RuntimeError(f"Error connecting to MongoDB: {e}")

    @staticmethod
    def close() -> None:
        """Close MongoDB connections"""
        if Database._client is not None:
            Database._client.close()
        if Database._sync_client is not None:
            Database._sync_client.close()
        Database._client = None
        Database._sync_client = None
        Database._db = None
        Database._sync_db = None
        Database._is_connected = False

    @staticmethod
    def get_connection_info() -> dict:
        """Get connection information for verification"""
        return {
            "is_connected": Database._is_connected,
            "connection_count": Database._connection_count,
            "has_async_client": Database._client is not None,
            "has_sync_client": Database._sync_client is not None,
            "has_db": Database._db is not None,
            "has_sync_db": Database._sync_db is not None,
            "async_client_id": id(Database._client) if Database._client else None,
            "sync_client_id": id(Database._sync_client) if Database._sync_client else None,
        }

    @staticmethod
    def get_db() -> AsyncIOMotorDatabase:
        """Get async database instance"""
        if Database._db is None:
            raise RuntimeError("MongoDB database not initialized. Call Database.connect() first.")
        return Database._db

    @staticmethod
    def get_sync_db() -> PyMongoDatabase:
        """Get sync database instance (for legacy code that uses pymongo)"""
        if Database._sync_db is None:
            raise RuntimeError("MongoDB sync database not initialized. Call Database.connect() first.")
        return Database._sync_db


# Convenience functions for backward compatibility
def connect() -> None:
    Database.connect()


def close() -> None:
    Database.close()


def get_db() -> AsyncIOMotorDatabase:
    return Database.get_db()


def get_sync_db() -> PyMongoDatabase:
    return Database.get_sync_db()


def get_connection_info() -> dict:
    return Database.get_connection_info()
