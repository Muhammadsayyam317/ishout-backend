from app.models.user_model import (
    PasswordChangeRequest,
    UserUpdateRequest,
)
from app.api.controllers.auth_controller import (
    get_user_profile,
    update_user_profile,
    change_password,
)
from fastapi import APIRouter, HTTPException, Depends
from app.middleware.auth_middleware import require_company_user_access

router = APIRouter()


@router.put("/profile", tags=["User"])
async def update_profile_route(
    request_data: UserUpdateRequest,
    current_user: dict = Depends(require_company_user_access),
):
    """Update user profile (Company users only)"""
    try:
        return await update_user_profile(current_user["user_id"], request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", tags=["User"])
async def get_profile_route(current_user: dict = Depends(require_company_user_access)):
    """Get current user profile (Company users only)"""
    try:
        return await get_user_profile(current_user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/change-password", tags=["User"])
async def change_password_route(
    request_data: PasswordChangeRequest,
    current_user: dict = Depends(require_company_user_access),
):
    """Change user password (Company users only)"""
    try:
        return await change_password(current_user["user_id"], request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
