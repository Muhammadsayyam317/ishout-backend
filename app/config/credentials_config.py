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
    MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS: str = Field(
        default=os.getenv("MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS")
    )
    MONGODB_COLLECTION_WHATSAPP_MESSAGES: str = Field(
        default=os.getenv("MONGODB_COLLECTION_WHATSAPP_MESSAGES")
    )
    MONGODB_ATLAS_COLLECTION_GENERATED_INFLUENCERS: str = Field(
        default=os.getenv("MONGO_ATLAS_GENERATED_INFLUENCER")
    )
    INSTAGRAM_MESSAGE_COLLECTION: str = Field(
        default=os.getenv("MONGODB_COLLECTION_INSTAGRAM_MESSAGES")
    )
    MONGODB_AGENT_CONTROL: str = Field(
        default=os.getenv("MONGODB_AGENT_CONTROL", "agent_controls")
    )
    MONGODB_NEGOTIATION_AGENT_CONTROLS: str = Field(
        default=os.getenv(
            "MONGODB_NEGOTIATION_AGENT_CONTROLS", "negotiation_agent_controls"
        )
    )
    MONGODB_WHATSAPP_ADMIN_INFLUENCER: str = Field(
        default=os.getenv(
            "MONGODB_WHATSAPP_ADMIN_INFLUENCER", "whatsapp_admin_influencer"
        )
    )
    MONGODB_WHATSAPP_ADMIN_COMPANY: str = Field(
        default=os.getenv(
            "MONGODB_WHATSAPP_ADMIN_COMPANY", "whatsapp_admin_company"
        )
    )
    MONGODB_CONTENT_FEEDBACK: str = Field(
        default=os.getenv("MONGODB_CONTENT_FEEDBACK", "content_feedback")
    )
    MONGODB_APPROVED_CONTENT: str = Field(
        default=os.getenv("MONGODB_APPROVED_CONTENT", "approved_content")
    )
    MONGODB_CAMPAIGN_BRIEF_GENERATION: str = Field(
        default=os.getenv("MONGODB_CAMPAIGN_BRIEF_GENERATION", "CampaignBriefGeneration")
    )
    MONGODB_WHATSAPP_NEGOTIATION: str = Field(
        default=os.getenv("MONGODB_WHATSAPP_NEGOTIATION", "whatsapp_negotiation")
    )
    MONGODB_INSTAGRAM_SESSIONS: str = Field(
        default=os.getenv("MONGODB_INSTAGRAM_SESSIONS", "instagram_sessions")
    )
    MONGODB_GUARDRAIL_LOGS: str = Field(
        default=os.getenv("MONGODB_GUARDRAIL_LOGS", "guardrail_logs")
    )
    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY"))
    OPENAI_MODEL_NAME: str = Field(default=os.getenv("OPENAI_MODEL_NAME"))
    OPENAI_GPT_IMAGE_MODEL: str = Field(default=os.getenv("OPENAI_GPT_IMAGE_MODEL"))

    EMBEDDING_MODEL: str = Field(default=os.getenv("EMBEDDING_MODEL"))
    PORT: int = Field(default=int(os.getenv("PORT", "8000")))

    JWT_SECRET_KEY: str = Field(default=os.getenv("JWT_SECRET_KEY"))
    JWT_ALGORITHM: str = Field(default=os.getenv("JWT_ALGORITHM", "HS256"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    )

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
    IG_BUSINESS_ID: str = Field(default=os.getenv("IG_BUSINESS_ID"))
    INSTAGRAM_PAGE_ACCESS_TOKEN: str = Field(
        default=os.getenv("INSTAPAGE_ACCESS_TOKEN")
    )

    REDIS_URL: str = Field(default=os.getenv("REDIS_URL"))
    RESEND_FROM_EMAIL: str = Field(default=os.getenv("RESEND_FROM_EMAIL"))
    RESEND_API_KEY: str = Field(default=os.getenv("RESEND_API_KEY"))

    REGISTER_URL: str = Field(default=os.getenv("REGISTER_URL"))
    ADMIN_PHONE: str = Field(default=os.getenv("ADMIN_PHONE"))

    FRONTEND_URL: str = Field(default=os.getenv("FRONTEND_URL"))
    VERIFY_OTP_URL: str = Field(default=os.getenv("VERIFY_OTP_URL"))

    AWS_ACCESS_KEY_ID: str = Field(default=os.getenv("AWS_ACCESS_KEY_ID"))
    AWS_SECRET_ACCESS_KEY: str = Field(default=os.getenv("AWS_SECRET_ACCESS_KEY"))
    AWS_REGION: str = Field(default=os.getenv("AWS_REGION"))
    S3_BUCKET_NAME: str = Field(default=os.getenv("S3_BUCKET_NAME"))

    MESSAGE_FROM: str = Field(default=os.getenv("MESSAGE_FROM"))



# config singleton instance
config = Config()
