import httpx
from datetime import datetime, timezone
from app.config.credentials_config import config
from typing import Optional
from app.utils.campaign_helpers import upload_file_to_s3_with_prefix

async def upload_whatsapp_media_to_s3(media_id: str, media_type: str, mime_type: str) -> Optional[str]:
    """
    Downloads media from Meta Graph API using media_id, then uploads it to S3.
    Returns the S3 URL if successful, else None.
    """
    try:
        # Step 1: Fetch Media URL from Meta
        whatsapp_token = config.META_WHATSAPP_ACCESSSTOKEN
        api_version = config.WHATSAPP_GRAPH_API_VERSION or "v19.0"
        
        meta_url = f"https://graph.facebook.com/{api_version}/{media_id}"
        headers = {"Authorization": f"Bearer {whatsapp_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(meta_url, headers=headers)
            response.raise_for_status()
            media_info = response.json()
            download_url = media_info.get("url")
            
            if not download_url:
                print(f"[upload_whatsapp_media_to_s3] No download URL found for media_id {media_id}")
                return None
            
            # Step 2: Download Media Binary
            # Use the same token for the download
            media_response = await client.get(download_url, headers=headers)
            media_response.raise_for_status()
            binary_content = media_response.content
        
        # Step 3: Upload to S3 using existing helper from campaign_helpers
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Derive filename for extension detection in upload_file_to_s3_with_prefix
        ext = mime_type.split("/")[-1] if "/" in mime_type else "bin"
        if "ogg" in mime_type:
            ext = "ogg"
        elif "jpeg" in mime_type:
            ext = "jpg"
            
        s3_url = await upload_file_to_s3_with_prefix(
            prefix_folder=f"whatsapp-media/{media_type}/{date_str}",
            object_id=media_id,
            file_bytes=binary_content,
            filename=f"media.{ext}",
            content_type=mime_type
        )
        
        return s3_url

    except Exception as e:
        print(f"[upload_whatsapp_media_to_s3] Error: {e}")
        return None
