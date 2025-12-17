from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.api.controllers.admin.campaign_controller import update_status
from app.api.controllers.admin.onboarding_influencers import (
    onboarding_campaigns,
)
from app.api.controllers.admin.approved_campaign import (
    approved_campaign,
    approvedAdminCampaignById,
)
from app.api.controllers.admin.campaign_byId import campaign_by_id_controller
from app.api.controllers.admin.delete_campaign import delete_campaign_ById
from app.api.controllers.admin.delete_influencers import deleteInfluencerEmbedding
from app.api.controllers.admin.campaign_controller import (
    AdminApprovedSingleInfluencer,
    company_approved_campaign_influencers,
    get_all_campaigns,
    admin_generate_influencers,
    get_campaign_generated_influencers,
    update_campaignstatus_with_background_task,
)

from app.api.controllers.admin.reject_regenerate_influencers import (
    reject_and_regenerate,
)
from app.api.controllers.company.company_data import company_data
from app.models.campaign_model import (
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
    RejectInfluencersRequest,
)
from app.middleware.auth_middleware import require_admin_access

router = APIRouter()

router.add_api_route(
    path="/campaigns",
    endpoint=get_all_campaigns,
    methods=["GET"],
    tags=["Admin"],
)


router.add_api_route(
    path="/company-data/{user_id}",
    endpoint=company_data,
    methods=["GET"],
    tags=["Admin"],
)


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
    endpoint=approvedAdminCampaignById,
    methods=["GET"],
    tags=["Admin"],
)


router.add_api_route(
    path="/campaigns/update-influencer-status",
    endpoint=AdminApprovedSingleInfluencer,
    methods=["PATCH"],
    tags=["Admin"],
)


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
    try:
        return get_campaign_generated_influencers(campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/update-status", tags=["Admin"])
async def update_campaign_status_route(
    request_data: CampaignStatusUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await update_campaignstatus_with_background_task(
            request_data, background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/campaigns/status-update", tags=["Admin"])
async def update_status_route(
    request_data: CampaignStatusUpdateRequest,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await update_status(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaigns/reject-and-regenerate", tags=["Admin"])
async def reject_and_regenerate_route(
    request_data: RejectInfluencersRequest,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await reject_and_regenerate(request_data)
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
router.add_api_route(
    path="/delete-influencer",
    endpoint=deleteInfluencerEmbedding,
    methods=["DELETE"],
    tags=["Admin"],
)
router.add_api_route(
    path="/company-approved-influencers/{campaign_id}",
    endpoint=company_approved_campaign_influencers,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/onboarding-campaigns",
    endpoint=onboarding_campaigns,
    methods=["GET"],
    tags=["Admin"],
)
