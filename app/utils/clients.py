from langfuse import Langfuse
from openai import OpenAI
from app.config import config
import boto3


def get_openai_client():
    openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    return openai_client


def get_langfuse_client():
    langfuse_client = Langfuse(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        secret_key=config.LANGFUSE_SECRET_KEY,
        host=config.LANGFUSE_BASE_URL,
    )
    return langfuse_client


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )


def upload_to_s3(s3_client, key: str, body: bytes, content_type: str = "image/png"):
    s3_client.put_object(
        Bucket=config.S3_BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType=content_type,
    )
