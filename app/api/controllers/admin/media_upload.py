"""
media_upload.py — Admin media upload controller.
Flow:
  1. Admin POSTs a file to POST /api/admin/upload-media
  2. Backend uploads to S3 → permanent S3 URL
  3. Backend uploads to Meta Media API → transient meta_media_id (for sending)
  4. Returns { s3_url, meta_media_id, media_type, media_filename } to admin
  5. Admin uses meta_media_id in their send-human-message call
"""
import httpx
from fastapi import UploadFile, File
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.utils.campaign_helpers import upload_file_to_s3_with_prefix
import uuid

SUPPORTED_MIME_TYPES = {
    # images
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    # video
    "video/mp4": "video",
    "video/3gpp": "video",
    # audio
    "audio/aac": "audio",
    "audio/mpeg": "audio",
    "audio/ogg": "audio",
    "audio/opus": "audio",
    # documents
    "application/pdf": "document",
    "application/msword": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "text/plain": "document",
}

META_MEDIA_UPLOAD_URL = (
    f"https://graph.facebook.com/v22.0/{config.WHATSAPP_PHONE_NUMBER}/media"
)


async def upload_admin_media(file: UploadFile = File(...)):
    """
    Step 1: Upload admin-submitted file to S3 (permanent) + Meta (transient for sending).
    Returns { s3_url, meta_media_id, media_type, media_filename }.
    """
    mime_type = file.content_type or "application/octet-stream"
    media_type = SUPPORTED_MIME_TYPES.get(mime_type)
    if not media_type:
        raise InternalServerErrorException(
            message=f"Unsupported file type: {mime_type}. "
                    f"Supported: {', '.join(SUPPORTED_MIME_TYPES.keys())}"
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise InternalServerErrorException(message="Empty file uploaded")

    filename = file.filename or f"upload_{uuid.uuid4()}"

    # --- 1. Upload to S3 (permanent record) ---
    try:
        s3_url = await upload_file_to_s3_with_prefix(
            prefix_folder="chat_media",
            object_id=str(uuid.uuid4()),
            file=file,
            file_bytes=file_bytes,
            filename=filename,
            content_type=mime_type,
        )
    except Exception as e:
        raise InternalServerErrorException(
            message=f"S3 upload failed: {str(e)}"
        ) from e

    # --- 2. Upload to Meta Media API (transient, for sending only) ---
    try:
        headers = {"Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                META_MEDIA_UPLOAD_URL,
                headers=headers,
                files={
                    "file": (filename, file_bytes, mime_type),
                    "type": (None, mime_type),
                    "messaging_product": (None, "whatsapp"),
                },
            )
        if response.status_code != 200:
            raise InternalServerErrorException(
                message=f"Meta media upload failed: {response.status_code} {response.text}"
            )
        meta_media_id = response.json().get("id")
        if not meta_media_id:
            raise InternalServerErrorException(
                message="Meta media upload succeeded but returned no media ID"
            )
    except InternalServerErrorException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Meta media upload error: {str(e)}"
        ) from e

    return {
        "success": True,
        "s3_url": s3_url,
        "meta_media_id": meta_media_id,
        "media_type": media_type,
        "media_filename": filename,
        "media_mime_type": mime_type,
    }
