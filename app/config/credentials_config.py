import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    DATABASE_URL: str = Field(default=os.getenv("MONGODB_ATLAS_URI"))
    DB_NAME: str = Field(default=os.getenv("MONGODB_ATLAS_DB_NAME"))

    TWILIO_ACCOUNT_SID: str = Field(default=os.getenv("TWILIO_ACCOUNT_SID"))
    TWILIO_AUTH_TOKEN: str = Field(default=os.getenv("TWILIO_AUTH_TOKEN"))
    TWILLIO_NUMBER: str = Field(default=os.getenv("TWILLIO_NUMBER"))

    MONGODB_ATLAS_URI: str = Field(default=os.getenv("MONGODB_ATLAS_URI"))
    MONGODB_ATLAS_DB_NAME: str = Field(default=os.getenv("MONGODB_ATLAS_DB_NAME"))

    MONGODB_ATLAS_COLLECTION_INFLUENCERS: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_INFLUENCERS")
    )
    MONGODB_ATLAS_COLLECTION_TIKTOK: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
    )
    MONGODB_ATLAS_COLLECTION_YOUTUBE: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
    )

    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY"))
    EMBEDDING_MODEL: str = Field(default=os.getenv("EMBEDDING_MODEL"))
    PORT: int = Field(default=int(os.getenv("PORT")))

    JWT_SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY"))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
    )


# config singleton instance
config = Config()
