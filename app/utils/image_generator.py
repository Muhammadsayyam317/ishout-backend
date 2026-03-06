import base64
import uuid
from fastapi import HTTPException
from app.config.credentials_config import config
from app.utils.prompts import CAMPAIGN_LOGO_PROMPT
from app.utils.clients import get_openai_client, get_s3_client, upload_to_s3


client = get_openai_client()
s3_client = get_s3_client()


async def generate_campaign_logo(
    title: str,
    overview: str,
    brand_name_influencer_campaign_brief: str,
) -> str | None:
    try:
        prompt = CAMPAIGN_LOGO_PROMPT.format(
            title=title,
            overview=overview,
            brand_name_influencer_campaign_brief=brand_name_influencer_campaign_brief,
        )
        result = client.images.generate(
            model=config.OPENAI_GPT_IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
        )
        if not result.data or not result.data[0].b64_json:
            raise HTTPException(status_code=500, detail="OpenAI returned no image")
        
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        unique_id = str(uuid.uuid4())
        s3_key = f"campaign_logos/{brief_id}_{unique_id}.png"

        upload_to_s3(s3_client, s3_key, image_bytes)
        logo_url = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
        return logo_url

    except HTTPException:
        raise
    except Exception as e:
        print("Logo generation/upload failed:", str(e))
        return None
