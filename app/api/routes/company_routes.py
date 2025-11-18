from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.api.controllers.auth_controller import (
    get_user_profile,
    update_user_profile,
    change_password,
    get_user_campaigns,
)
from app.api.controllers.company.approved_influencers import (
    get_company_approved_influencers,
)
from app.models.user_model import (
    PasswordChangeRequest,
    UserUpdateRequest,
)
from app.middleware.auth_middleware import require_company_user_access
from app.api.controllers.campaign_controller import (
    create_campaign,
    get_campaign_by_id,
    user_reject_influencers,
    approve_single_influencer,
)
from app.models.campaign_model import (
    CreateCampaignRequest,
    UserRejectInfluencersRequest,
)
from app.models.campaign_influencers_model import CampaignInfluencersRequest
from app.tools.search_influencers import search_influencers

router = APIRouter()


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
    current_user: dict = Depends(require_company_user_access),
):
    """Update user profile (Company users only)"""
    try:
        return await update_user_profile(current_user["user_id"], request_data)
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


@router.post("/campaigns", tags=["User"])
async def create_campaign_route(
    request_data: CreateCampaignRequest,
    current_user: dict = Depends(require_company_user_access),
):
    try:
        request_data.user_id = current_user["user_id"]
        return await create_campaign(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", tags=["User"])
async def get_user_campaigns_route(
    status: Optional[str] = None,
    current_user: dict = Depends(require_company_user_access),
):
    """Get user's campaigns with approved influencers (Company users only). Optional query param: status"""
    try:
        return await get_user_campaigns(current_user["user_id"], status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/reject-influencers", tags=["User"])
async def reject_influencers_route(
    request_data: UserRejectInfluencersRequest,
    current_user: dict = Depends(require_company_user_access),
):
    """Reject approved influencers for a campaign (Company users only)"""
    try:
        return await user_reject_influencers(
            request_data.campaign_id,
            request_data.influencer_ids,
            current_user["user_id"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/campaigns/update-influencer-status", tags=["User"])
async def approve_single_influencer_company_route(
    request_data: CampaignInfluencersRequest,
    current_user: dict = Depends(require_company_user_access),
):
    """Approve or reject a single influencer (Company users only)"""
    try:
        return await approve_single_influencer(request_data, current_user["role"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/approved-influencers", tags=["User"])
async def get_campaign_approved_influencers_route(
    campaign_id: str, current_user: dict = Depends(require_company_user_access)
):
    try:
        campaign_data = await get_campaign_by_id(campaign_id)
        if "error" in campaign_data:
            raise HTTPException(status_code=400, detail="Campaign not found")
        campaign = campaign_data.get("campaign", {})
        if campaign.get("user_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to view this campaign",
            )

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
                "updated_at": campaign.get("updated_at"),
            },
            "approved_influencers": campaign_data.get("approved_influencers", []),
            "rejected_by_user_influencers": campaign_data.get(
                "rejected_by_user_influencers", []
            ),
            "total_approved": campaign_data.get("total_approved", 0),
            "total_rejected_by_user": campaign_data.get("total_rejected_by_user", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router.add_api_route(
    path="/search-influencers",
    endpoint=search_influencers,
    methods=["POST"],
    tags=["User"],
)

router.add_api_route(
    path="/approved-campaigns/{user_id}",
    endpoint=get_company_approved_influencers,
    methods=["GET"],
    tags=["Company"],
)
