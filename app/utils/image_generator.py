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
    title: str, overview: str, brand_name_influencer_campaign_brief: str
) -> str | None:
    """
    Generate a majestic, circular campaign logo using OpenAI Images
    and upload it to S3. Returns the public URL of the uploaded logo.
    """
    try:
        prompt = f"""
        Create a premium, photorealistic circular brand logo for a campaign.

        Campaign Title: {title}
        Campaign Description: {overview}
        Brand / Influencer Campaign Context: {brand_name_influencer_campaign_brief}

        CRITICAL REQUIREMENTS:
        - **ABSOLUTELY NO TEXT, NO LETTERS, NO WORDS, NO TYPOGRAPHY** - pure visual symbol only
        - Photorealistic, professional corporate identity style
        - NOT cartoon, NOT animated, NOT illustrated - real luxury brand aesthetic
        - Circular emblem design centered on 1024x1024 canvas
        - High-end, premium, sophisticated visual language
        - Think Apple, Nike, Mercedes - iconic symbol only
        - Clean, minimalist, timeless design
        - Professional gradient or solid color palette
        - Suitable for Fortune 500 brand identity
        - Sharp, crisp edges with depth and dimension
        - Metallic, glass, or premium material effects
        - Studio lighting, professional photography quality
        - Symbol must relate to campaign theme through abstract shapes, icons, or imagery
        - Recognizable and memorable at any size

        STYLE REFERENCES: Corporate logo design, luxury brand identity, premium product photography, high-end advertising
        
        AVOID: Cartoons, comics, hand-drawn, sketches, childish, playful, text overlays, words, letters
        """

        result = client.images.generate(
            model="gpt-image-1", prompt=prompt, size="1024x1024"
        )

        image_base64 = result.data[0].b64_json
        if not image_base64:
            raise HTTPException(status_code=500, detail="OpenAI returned no image")

        image_bytes = base64.b64decode(image_base64)

        unique_id = str(uuid.uuid4())
        s3_key = f"campaign_logos/{unique_id}.png"

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
