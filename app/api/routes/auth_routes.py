from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
from app.api.controllers.auth_controller import (
    register_company,
    login_user,
    get_user_profile,
    update_user_profile,
    change_password,
    get_user_campaigns,
    get_current_user
)
from app.models.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
    PasswordChangeRequest,
    UserUpdateRequest
)
from app.middleware.auth_middleware import get_authenticated_user, security, require_company_user_access
from app.api.controllers.campaign_controller import create_campaign, get_campaign_by_id
from app.models.campaign_model import CreateCampaignRequest

router = APIRouter()


@router.post("/register", tags=["Auth"])
async def register_route(request_data: CompanyRegistrationRequest):
    """Register a new company"""
    try:
        return await register_company(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", tags=["Auth"])
async def login_route(request_data: UserLoginRequest):
    """Login user"""
    try:
        return await login_user(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", tags=["User"])
async def get_profile_route(current_user: dict = Depends(require_company_user_access)):
    """Get current user profile (Company users only)"""
    try:
        return await get_user_profile(current_user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", tags=["User"])
async def update_profile_route(
    request_data: UserUpdateRequest,
    current_user: dict = Depends(require_company_user_access)
):
    """Update user profile (Company users only)"""
    try:
        return await update_user_profile(current_user["user_id"], request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/change-password", tags=["User"])
async def change_password_route(
    request_data: PasswordChangeRequest,
    current_user: dict = Depends(require_company_user_access)
):
    """Change user password (Company users only)"""
    try:
        return await change_password(current_user["user_id"], request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns", tags=["User"])
async def create_campaign_route(
    request_data: CreateCampaignRequest,
    current_user: dict = Depends(require_company_user_access)
):
    """Create a new campaign (Company users only - not admins)"""
    try:
        # Add user_id to request
        request_data.user_id = current_user["user_id"]
        
        return await create_campaign(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", tags=["User"])
async def get_user_campaigns_route(current_user: dict = Depends(require_company_user_access)):
    """Get user's campaigns with approved influencers (Company users only)"""
    try:
        return await get_user_campaigns(current_user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/approved-influencers", tags=["User"])
async def get_campaign_approved_influencers_route(
    campaign_id: str,
    current_user: dict = Depends(require_company_user_access)
):
    """Get approved influencers for a specific campaign (Company users only)"""
    try:
        # Get campaign details with influencers
        campaign_data = await get_campaign_by_id(campaign_id)
        
        # Check if campaign exists
        if "error" in campaign_data:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Verify the campaign belongs to the user
        campaign = campaign_data.get("campaign", {})
        if campaign.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="You don't have permission to view this campaign")
        
        # Return campaign with ONLY approved influencers (not rejected or generated)
        return {
            "campaign": {
                "campaign_id": campaign_id,
                "name": campaign.get("name"),
                "description": campaign.get("description"),
                "status": campaign.get("status"),
                "platform": campaign.get("platform"),
                "category": campaign.get("category"),
                "followers": campaign.get("followers"),
                "country": campaign.get("country"),
                "created_at": campaign.get("created_at"),
                "updated_at": campaign.get("updated_at")
            },
            "approved_influencers": campaign_data.get("approved_influencers", []),
            "total_approved": campaign_data.get("total_approved", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
