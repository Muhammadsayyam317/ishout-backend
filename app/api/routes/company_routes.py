from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.api.controllers.admin.approved_campaign import companyApprovedSingleInfluencer
from app.api.controllers.auth_controller import (
    get_user_profile,
    get_user_campaigns,
)

from app.middleware.auth_middleware import require_company_user_access
from app.api.controllers.campaign_controller import (
    create_campaign,
    get_campaign_by_id,
    user_reject_influencers,
)
from app.models.campaign_model import (
    CreateCampaignRequest,
    UserRejectInfluencersRequest,
)
from app.tools.search_influencers import search_influencers

router = APIRouter()


@router.get("/profile", tags=["User"])
async def get_profile_route(current_user: dict = Depends(require_company_user_access)):
    """Get current user profile (Company users only)"""
    try:
        return await get_user_profile(current_user["user_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns", tags=["Company"])
async def create_campaign_route(
    request_data: CreateCampaignRequest,
    current_user: dict = Depends(require_company_user_access),
):
    try:
        request_data.user_id = current_user["user_id"]
        return await create_campaign(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns", tags=["Company"])
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


router.add_api_route(
    path="/campaigns/update-influencer-status",
    endpoint=companyApprovedSingleInfluencer,
    methods=["PATCH"],
    tags=["Company"],
)


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
    endpoint=companyApprovedSingleInfluencer,
    methods=["GET"],
    tags=["Company"],
)
