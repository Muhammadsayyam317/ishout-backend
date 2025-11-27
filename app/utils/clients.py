from langfuse import Langfuse
from openai import OpenAI
from app.config import config


def get_openai_client():
    """Return the initialized OpenAI client."""
    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    return openai_client


def get_langfuse_client():
    """Return the initialized LangFuse client."""
    langfuse_client = Langfuse(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        secret_key=config.LANGFUSE_SECRET_KEY,
        host=config.LANGFUSE_HOST,
    )
    return langfuse_client
