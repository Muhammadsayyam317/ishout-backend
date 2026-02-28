from typing import Dict, Any
from fastapi import HTTPException, UploadFile
from app.Schemas.user_model import UserLoginRequest, CompanyRegistrationRequest
from app.services.Auth.auth_service import AuthService
from app.services.email.email_verification import send_verification_email
from app.core.security.jwt import create_email_verification_token, verify_token
from app.core.exception import UnauthorizedException
from bson import ObjectId
from app.model.user_model import UserModel
from app.config import config
import boto3
import uuid

s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION,
)


async def login_user(request_data: UserLoginRequest) -> Dict[str, Any]:
    try:
        return await AuthService.login(request_data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=e.detail["message"])


async def register_company(
    request_data: CompanyRegistrationRequest,
) -> Dict[str, Any]:
    response = await AuthService.register_company(request_data)
    verification_token = create_email_verification_token({"email": request_data.email})
    await send_verification_email(
        [request_data.email],
        "Verify your Ishout account",
        request_data.company_name,
        verification_token,
    )
    return response


async def upload_user_logo(user_id: str, file: UploadFile):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Only PNG or JPEG images are allowed",
        )

    user = await UserModel.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    unique_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()

    s3_key = f"users/logos/{user_id}_{unique_id}.{extension}"
    try:
        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
    file_url = (
        f"https://{config.S3_BUCKET_NAME}.s3."
        f"{config.AWS_REGION}.amazonaws.com/{s3_key}"
    )
    await UserModel.update_logo(user_id, file_url)
    return {
        "message": "Logo uploaded successfully",
        "logo_url": file_url,
    }


async def get_current_user(token: str) -> Dict[str, Any]:
    try:
        payload = verify_token(token)
        if not payload:
            raise UnauthorizedException(message="Invalid token")
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
