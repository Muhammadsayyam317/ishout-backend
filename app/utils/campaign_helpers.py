from typing import Optional

from fastapi import HTTPException, UploadFile

from app.config.credentials_config import config
from app.utils.image_generator import s3_client
import uuid


async def validate_and_read_image_file(file: UploadFile) -> bytes:
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Only PNG or JPEG images are allowed",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    return file_bytes


def delete_s3_object_if_exists(existing_logo_url: Optional[str]) -> None:
    prefix = (
        f"https://{config.S3_BUCKET_NAME}.s3."
        f"{config.AWS_REGION}.amazonaws.com/"
    )

    if existing_logo_url and existing_logo_url.startswith(prefix):
        old_key = existing_logo_url[len(prefix):]
        try:
            s3_client.delete_object(
                Bucket=config.S3_BUCKET_NAME,
                Key=old_key,
            )
        except Exception as e:
            # Log but do not fail the whole operation if delete fails
            print(
                "[campaign_helpers] Failed to delete old logo from S3: "
                f"{e}"
            )


async def upload_file_to_s3_with_prefix(
    prefix_folder: str,
    object_id: str,
    file: UploadFile,
    file_bytes: bytes,
) -> str:
    prefix = (
        f"https://{config.S3_BUCKET_NAME}.s3."
        f"{config.AWS_REGION}.amazonaws.com/"
    )

    extension = file.filename.split(".")[-1].lower()
    unique_id = str(uuid.uuid4())
    s3_key = f"{prefix_folder}/{object_id}_{unique_id}.{extension}"

    try:
        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

    logo_url = prefix + s3_key
    return logo_url

