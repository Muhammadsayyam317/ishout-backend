"""
Centralized configuration module for loading and managing environment variables.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration class for all environment variables"""
    
    # MongoDB Configuration
    MONGODB_ATLAS_URI: str = os.getenv("MONGODB_ATLAS_URI", "")
    MONGODB_ATLAS_DB_NAME: str = os.getenv("MONGODB_ATLAS_DB_NAME", "")
    MONGODB_ATLAS_COLLECTION_INSTAGRAM: str = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM", "")
    MONGODB_ATLAS_COLLECTION_TIKTOK: str = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK", "")
    MONGODB_ATLAS_COLLECTION_YOUTUBE: str = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE", "")
    MONGODB_VECTOR_INDEX_NAME: str = os.getenv("MONGODB_VECTOR_INDEX_NAME", "vector_index")
    MONGODB_TEXT_KEY: str = os.getenv("MONGODB_TEXT_KEY", "text")
    MONGODB_EMBEDDING_KEY: str = os.getenv("MONGODB_EMBEDDING_KEY", "embedding")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @classmethod
    def get_collection_name(cls, platform: str) -> Optional[str]:
        """
        Get collection name for a given platform.
        
        Args:
            platform: Platform name (instagram, tiktok, youtube)
            
        Returns:
            Collection name or None if platform is invalid
        """
        platform_lower = platform.lower().strip()
        if platform_lower == "instagram":
            return cls.MONGODB_ATLAS_COLLECTION_INSTAGRAM
        elif platform_lower == "tiktok":
            return cls.MONGODB_ATLAS_COLLECTION_TIKTOK
        elif platform_lower == "youtube":
            return cls.MONGODB_ATLAS_COLLECTION_YOUTUBE
        return None
    
    @classmethod
    def validate_required(cls) -> list:
        """
        Validate that all required configuration values are set.
        
        Returns:
            List of missing required configuration keys
        """
        required_vars = [
            ("MONGODB_ATLAS_URI", cls.MONGODB_ATLAS_URI),
            ("MONGODB_ATLAS_DB_NAME", cls.MONGODB_ATLAS_DB_NAME),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing = []
        for key, value in required_vars:
            if not value:
                missing.append(key)
        
        return missing


# Create a singleton instance
config = Config()

