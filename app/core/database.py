from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from app.config import config


class DatabaseConnection:
    """Singleton class for managing database connections"""
    
    _instance: Optional['DatabaseConnection'] = None
    _async_client: Optional[AsyncIOMotorClient] = None
    _sync_client: Optional[MongoClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    _sync_db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    async def connect(self) -> AsyncIOMotorDatabase:
    
        if self._async_client is None:
            if not config.MONGODB_ATLAS_URI:
                raise ValueError("MongoDB URI not found in environment variables. Check MONGODB_ATLAS_URI.")
            
            if not config.MONGODB_ATLAS_DB_NAME:
                raise ValueError("MongoDB database name not found in environment variables. Check MONGODB_ATLAS_DB_NAME.")
            
            self._async_client = AsyncIOMotorClient(config.MONGODB_ATLAS_URI)
            self._sync_client = MongoClient(config.MONGODB_ATLAS_URI)
            
            self._db = self._async_client[config.MONGODB_ATLAS_DB_NAME]
            self._sync_db = self._sync_client[config.MONGODB_ATLAS_DB_NAME]
            
            print(f"MongoDB connected (async and sync clients) ✅ - Database: {config.MONGODB_ATLAS_DB_NAME}")
        
        return self._db
    
    def get_async_db(self) -> AsyncIOMotorDatabase:
    
        if self._db is None:
            raise ValueError("Database connection not initialized. Call connect() first.")
        return self._db
    
    def get_sync_db(self) -> Database:

        if self._sync_db is None:
            raise ValueError("Database connection not initialized. Call connect() first.")
        return self._sync_db
    
    async def disconnect(self):
        """Close database connections"""
        if self._async_client:
            self._async_client.close()
            self._async_client = None
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        self._db = None
        self._sync_db = None
        print("MongoDB connections closed")
    
    def get_collection(self, collection_name: str, use_async: bool = False):
     
        if use_async:
            db = self.get_async_db()
        else:
            db = self.get_sync_db()
        return db[collection_name]
    
    def get_platform_collection(self, platform: str, use_async: bool = False):
        collection_name = config.get_collection_name(platform)
        if not collection_name:
            raise ValueError(f"Invalid platform or collection name not configured for platform: {platform}")
        return self.get_collection(collection_name, use_async)


# Create singleton instance
db_connection = DatabaseConnection()


# Convenience functions for backward compatibility
async def connect_to_mongodb():
  
    return await db_connection.connect()


def get_db() -> AsyncIOMotorDatabase:
  
    return db_connection.get_async_db()


def get_sync_db() -> Database:
   
    return db_connection.get_sync_db()

