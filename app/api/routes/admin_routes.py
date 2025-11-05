from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from app.api.controllers.admin.approved_campaign import approved_campaign
from app.api.controllers.admin.delete_campaign import delete_campaign_ById
from app.api.controllers.campaign_controller import (
    get_all_campaigns,
    get_campaign_by_id,
    approve_single_influencer,
    approve_multiple_influencers,
    admin_generate_influencers,
    update_campaign_status,
    get_campaign_generated_influencers,
    reject_and_regenerate_influencers,
)
from app.models.campaign_model import (
    ApproveSingleInfluencerRequest,
    ApproveMultipleInfluencersRequest,
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
    RejectInfluencersRequest,
)
from app.api.controllers.auth_controller import get_current_user
from app.middleware.auth_middleware import require_admin_access

router = APIRouter()


@router.get("/campaigns", tags=["Admin"])
async def get_all_campaigns_route(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
    """Get all campaigns (admin only). Optional query params: status=pending|processing|completed, page=1, page_size=10"""
    try:
        return await get_all_campaigns(status, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-campaigns", tags=["Admin"])
async def get_pending_campaigns_route(
    status="pending",
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await get_all_campaigns(status, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processing-campaigns", tags=["Admin"])
async def get_processing_campaigns_route(
    status="processing",
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await get_all_campaigns(status, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        router.add_api_route(
            path="/approved-campaign",
            endpoint=approved_campaign,
            methods=["GET"],
            tags=["Admin"],
        )


@router.get("/campaigns/{campaign_id}", tags=["Admin"])
async def get_campaign_route(
    campaign_id: str, current_user: dict = Depends(require_admin_access)
):
    """Get campaign details by ID (admin only)"""
    try:
        return await get_campaign_by_id(campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/approve-single-influencer", tags=["Admin"])
async def approve_single_influencer_route(
    request_data: ApproveSingleInfluencerRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Approve a single influencer and add to campaign (admin only)"""
    try:
        return await approve_single_influencer(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/approve-multiple-influencers", tags=["Admin"])
async def approve_multiple_influencers_route(
    request_data: ApproveMultipleInfluencersRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Approve multiple influencers and add to campaign (admin only)"""
    try:
        return await approve_multiple_influencers(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/generate-influencers/{campaign_id}", tags=["Admin"])
async def generate_influencers_route(
    campaign_id: str,
    request_data: AdminGenerateInfluencersRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Generate influencers for a campaign (admin only)"""
    try:
        return await admin_generate_influencers(campaign_id, request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/generated-influencers", tags=["Admin"])
async def get_generated_influencers_route(
    campaign_id: str, current_user: dict = Depends(require_admin_access)
):
    """Get generated influencers for a campaign (admin only)"""
    try:
        return await get_campaign_generated_influencers(campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/update-status", tags=["Admin"])
async def update_campaign_status_route(
    request_data: CampaignStatusUpdateRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Update campaign status (admin only)"""
    try:
        return await update_campaign_status(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/reject-and-regenerate", tags=["Admin"])
async def reject_and_regenerate_route(
    request_data: RejectInfluencersRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Reject influencers and generate new ones (admin only)"""
    try:
        return await reject_and_regenerate_influencers(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router.add_api_route(
    path="/delete-campaign/{campaign_id}",
    endpoint=delete_campaign_ById,
    methods=["DELETE"],
    tags=["Admin"],
)
