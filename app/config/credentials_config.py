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

    MONGODB_ATLAS_COLLECTION_INSTAGRAM: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_INSTAGRAM")
    )
    MONGODB_ATLAS_COLLECTION_YOUTUBE: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
    )
    MONGODB_ATLAS_COLLECTION_TIKTOK: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
    )
    MONGODB_VECTOR_INDEX_NAME: str = Field(
        default=os.getenv("MONGODB_VECTOR_INDEX_NAME")
    )

    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY"))
    EMBEDDING_MODEL: str = Field(default=os.getenv("EMBEDDING_MODEL"))
    PORT: int = Field(default=int(os.getenv("PORT", "8000")))

    JWT_SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY"))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    )

    INSTAGRAM_APP_ID: str = Field(default=os.getenv("INSTAGRAM_APP_ID"))
    INSTAGRAM_APP_SECRET: str = Field(default=os.getenv("INSTAGRAM_APP_SECRET"))
    INSTAGRAM_REDIRECT_URL: str = Field(default=os.getenv("INSTAGRAM_REDIRECT_URL"))
    INSTAGRAM_ACCESS_TOKEN: str = Field(default=os.getenv("INSTAGRAM_ACCESS_TOKEN"))

    META_VERIFY_TOKEN: str = Field(default=os.getenv("META_VERIFY_TOKEN"))
    META_APP_SECRET: str = Field(default=os.getenv("META_APP_SECRET"))
    PAGE_ACCESS_TOKEN: str = Field(default=os.getenv("PAGE_ACCESS_TOKEN"))
    IG_GRAPH_API_VERSION: str = Field(default=os.getenv("IG_GRAPH_API_VERSION"))


# config singleton instance
config = Config()
