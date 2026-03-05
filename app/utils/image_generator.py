import base64
import uuid
from openai import OpenAI
from fastapi import HTTPException
from app.config.credentials_config import config
import boto3

s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION,
)

client = OpenAI(api_key=config.OPENAI_API_KEY)

async def generate_campaign_logo(
    title: str, 
    overview: str, 
    brand_name_influencer_campaign_brief: str
) -> str | None:
    """
    Generate a majestic, circular campaign logo using OpenAI Images
    and upload it to S3. Returns the public URL of the uploaded logo.
    """
    try:
        prompt = f"""
        Create a high-quality, circular campaign logo.

        Campaign Title: {title}
        Campaign Description: {overview}
        Brand / Influencer Campaign Context: {brand_name_influencer_campaign_brief}

        Requirements:
        - Circular / round design inside a square 1024x1024 canvas
        - Modern, elegant, and professional
        - Minimal text or subtle campaign initials
        - Visually represents the brand and campaign identity
        - Color palette inspired by fashion and lifestyle aesthetics
        - Suitable for social media cards, dashboards, and app listings
        - Clean lines, vector-style look, recognizable at small size
        """

        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        image_base64 = result.data[0].b64_json
        if not image_base64:
            raise HTTPException(status_code=500, detail="OpenAI returned no image")

        image_bytes = base64.b64decode(image_base64)

        unique_id = str(uuid.uuid4())
        s3_key = f"campaign_logos/{brief_id}_{unique_id}.png"

        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType="image/png",
        )

        logo_url = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"

        return logo_url

    except HTTPException:
        raise
    except Exception as e:
        print("Logo generation/upload failed:", str(e))
        return None