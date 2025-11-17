from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.api.controllers.admin.approved_campaign import (
    approved_campaign,
    approved_campaign_by_id,
)
from app.api.controllers.admin.campaign_byId import campaign_by_id_controller
from app.api.controllers.admin.delete_campaign import delete_campaign_ById
from app.api.controllers.campaign_controller import (
    get_all_campaigns,
    approve_single_influencer,
    admin_generate_influencers,
    update_campaign_status,
    get_campaign_generated_influencers,
    reject_and_regenerate_influencers,
)
from app.models.campaign_influencers_model import CampaignInfluencersRequest
from app.models.campaign_model import (
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
    RejectInfluencersRequest,
)
from app.middleware.auth_middleware import require_admin_access

# from app.services.email_service import send_mail

router = APIRouter()


@router.get("/campaigns", tags=["Admin"])
async def get_all_campaigns_route(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
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

router.add_api_route(
    path="/approved-campaign/{campaign_id}",
    endpoint=approved_campaign_by_id,
    methods=["GET"],
    tags=["Admin"],
)


@router.patch("/campaigns/update-influencer-status", tags=["Admin"])
async def approve_single_influencer_route(
    request_data: CampaignInfluencersRequest,
    current_user: dict = Depends(require_admin_access),
):
    """Approve or reject a single influencer (admin only)"""
    try:
        return await approve_single_influencer(request_data, current_user["role"])
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


router.add_api_route(
    path="/campaigns/{campaign_id}/generated-influencers",
    endpoint=get_campaign_generated_influencers,
    methods=["GET"],
    tags=["Admin"],
)


def get_generated_influencers_route(
    campaign_id: str, current_user: dict = Depends(require_admin_access)
):
    """Get generated influencers for a campaign (admin only)"""
    try:
        return get_campaign_generated_influencers(campaign_id)
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
    path="/campaigns/{campaign_id}",
    endpoint=campaign_by_id_controller,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/delete-campaign/{campaign_id}",
    endpoint=delete_campaign_ById,
    methods=["DELETE"],
    tags=["Admin"],
)


# @router.post("/send-email", tags=["Admin"])
# async def send_email_route(
#     to: List[str],
#     subject: str,
#     html: str,
#     current_user: dict = Depends(require_admin_access),
# ):
#     return await send_mail(to, subject, html)
