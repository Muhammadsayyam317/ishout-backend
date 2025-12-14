import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Config(BaseModel):
    DATABASE_URL: str = Field(default=os.getenv("MONGODB_ATLAS_URI"))
    DB_NAME: str = Field(default=os.getenv("MONGODB_ATLAS_DB_NAME"))

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
    MONGODB_ATLAS_COLLECTION_USERS: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_USERS")
    )
    MONGODB_ATLAS_COLLECTION_CAMPAIGNS: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_CAMPAIGNS")
    )
    MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS")
    )

    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY"))
    OPENAI_MODEL_NAME: str = Field(default=os.getenv("OPENAI_MODEL_NAME"))
    EMBEDDING_MODEL: str = Field(default=os.getenv("EMBEDDING_MODEL"))
    PORT: int = Field(default=int(os.getenv("PORT", "8000")))

    JWT_SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY"))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    )
    RESEND_API_KEY: str = Field(default=os.getenv("RESEND_API_KEY"))

    RECIPENT_NUMBER: str = Field(default=os.getenv("RECIPENT_NUMBER"))
    WHATSAPP_PHONE_NUMBER: str = Field(default=os.getenv("WHATSAPP_PHONE_NUMBER"))
    META_APP_ID: str = Field(default=os.getenv("META_APP_ID"))
    META_WHATSAP_APP_SECRET: str = Field(default=os.getenv("META_WHATSAP_APP_SECRET"))
    META_WHATSAPP_ACCESSSTOKEN: str = Field(
        default=os.getenv("META_WHATSAPP_ACCESSSTOKEN")
    )
    WHATSAPP_BUSSINESS_ACCOUNT_ID: str = Field(
        default=os.getenv("WHATSAPP_BUSSINESS_ACCOUNT_ID")
    )
    WHATSAPP_GRAPH_API_VERSION: str = Field(
        default=os.getenv("WHATSAPP_GRAPH_API_VERSION")
    )

    LANGFUSE_SECRET_KEY: str = Field(default=os.getenv("LANGFUSE_SECRET_KEY"))
    LANGFUSE_PUBLIC_KEY: str = Field(default=os.getenv("LANGFUSE_PUBLIC_KEY"))
    LANGFUSE_BASE_URL: str = Field(default=os.getenv("LANGFUSE_BASE_URL"))

    INSTAGRAM_APP_ID: str = Field(default=os.getenv("INSTAGRAM_APP_ID"))
    INSTAGRAM_APP_SECRET: str = Field(default=os.getenv("INSTAGRAM_APP_SECRET"))
    INSTAGRAM_REDIRECT_URL: str = Field(default=os.getenv("INSTAGRAM_REDIRECT_URL"))
    INSTAGRAM_ACCESS_TOKEN: str = Field(default=os.getenv("INSTAGRAM_ACCESS_TOKEN"))

    META_VERIFY_TOKEN: str = Field(default=os.getenv("META_VERIFY_TOKEN"))
    META_APP_SECRET: str = Field(default=os.getenv("META_APP_SECRET"))
    PAGE_ACCESS_TOKEN: str = Field(default=os.getenv("PAGE_ACCESS_TOKEN"))
    IG_GRAPH_API_VERSION: str = Field(default=os.getenv("IG_GRAPH_API_VERSION"))

    REDIS_HOST: str = Field(default=os.getenv("REDIS_HOST"))
    REDIS_PORT: int = Field(default=int(os.getenv("REDIS_PORT", "13814")))
    REDIS_USERNAME: str = Field(default=os.getenv("REDIS_USERNAME"))
    REDIS_PASSWORD: str = Field(default=os.getenv("REDIS_PASSWORD"))


# config singleton instance
config = Config()
