"""
send_media.py — WhatsApp outbound media sender.
Supports: image, video, audio, document.
The meta_media_id must already be uploaded to Meta (via upload-media endpoint).
S3 URL is the permanent record; meta_media_id is only used here transiently for sending.
"""
import httpx
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException

GRAPH_API_BASE = "https://graph.facebook.com/v22.0/967002123161751/messages"


async def send_whatsapp_media_message(
    to: str,
    meta_media_id: str,
    media_type: str,
    caption: str = "",
    filename: str | None = None,
) -> None:
    """
    Send a media message via WhatsApp Cloud API.

    Args:
        to: recipient phone number (e.g. "923001234567")
        meta_media_id: ID returned by Meta after uploading the file
        media_type: one of "image" | "video" | "audio" | "document"
        caption: optional caption displayed under the media
        filename: required for documents (shown as file name in WhatsApp)
    """
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    media_block: dict = {"id": meta_media_id}
    if caption and media_type in ("image", "video", "document"):
        media_block["caption"] = caption
    if media_type == "document" and filename:
        media_block["filename"] = filename

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: media_block,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(GRAPH_API_BASE, headers=headers, json=payload)
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"WhatsApp media send failed: {response.status_code} {response.text}"
                )
        except InternalServerErrorException:
            raise
        except Exception as e:
            raise InternalServerErrorException(
                message=f"Error sending WhatsApp media: {str(e)}"
            ) from e
