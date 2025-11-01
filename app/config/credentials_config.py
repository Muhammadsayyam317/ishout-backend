"""
Centralized Configuration Management
Loads all environment variables from .env file using dotenv (already installed)

This is a best practice because:
1. Single source of truth for all configuration
2. Easy to mock in tests
3. Centralized error handling for missing variables
4. IDE autocomplete support
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # MongoDB Configuration
    MONGODB_ATLAS_URI: str = os.getenv("MONGODB_ATLAS_URI") or ""
    MONGODB_ATLAS_DB_NAME: str = os.getenv("MONGODB_ATLAS_DB_NAME") or ""
    
    # MongoDB Collections
    MONGODB_ATLAS_COLLECTION_INSTGRAM: str = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM", "instagram")
    MONGODB_ATLAS_COLLECTION_TIKTOK: str = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK", "tiktok")
    MONGODB_ATLAS_COLLECTION_YOUTUBE: str = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE", "youtube")
    MONGODB_ATLAS_COLLECTION_INFLUENCERS: Optional[str] = os.getenv("MONGODB_ATLAS_COLLECTION_INFLUENCERS")
    
    # MongoDB Vector Store Configuration
    MONGODB_VECTOR_INDEX_NAME: str = os.getenv("MONGODB_VECTOR_INDEX_NAME", "vector_index")
    MONGODB_TEXT_KEY: str = os.getenv("MONGODB_TEXT_KEY", "text")
    MONGODB_EMBEDDING_KEY: str = os.getenv("MONGODB_EMBEDDING_KEY", "embedding")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY") or ""
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or ""
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILLIO_NUMBER: Optional[str] = os.getenv("TWILLIO_NUMBER")


# Create singleton instance
config = Config()
