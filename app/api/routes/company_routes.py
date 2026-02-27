from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Path
from app.Schemas.campaign_influencers import (
    CampaignBriefDBResponse,
    CampaignBriefRequest,
    CampaignBriefResponse,
    UpdateCampaignBriefRequest,
)
from app.api.controllers.admin.approved_campaign import (
    companyApprovedSingleInfluencer,
)
from app.api.controllers.auth.password_controller import change_password, reset_password
from app.api.controllers.company.all_campaign import (
    CompaignwithAdminApprovedInfluencersById,
    all_campaigns,
)
from app.api.controllers.company.approved_influencers import (
    ReviewPendingInfluencersByCampaignId,
)
from app.middleware.auth_middleware import require_company_user_access
from app.api.controllers.admin.campaign_controller import (
    create_campaign,
    user_reject_influencers,
)
from app.Schemas.campaign import (
    CreateCampaignRequest,
    UserRejectInfluencersRequest,
)
from typing import List
from app.services.whatsapp.send_text import send_message_from_ishout_to_user
from app.tools.search_influencers import search_influencers
from app.api.controllers.company.profile import get_user_profile, update_user_profile
from app.agents.campaiagncreation.create_campaign import (
    create_campaign_brief,
    get_campaign_brief_by_id,
    get_campaign_briefs,
    update_campaign_brief_service,
)

router = APIRouter()


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
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_company_user_access),
):
    try:
        return await all_campaigns(current_user["user_id"], status, page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/reject-influencers", tags=["Company"])
async def reject_influencers_route(
    request_data: UserRejectInfluencersRequest,
    current_user: dict = Depends(require_company_user_access),
):
    try:
        return await user_reject_influencers(
            request_data.campaign_id,
            request_data.influencer_ids,
            current_user["user_id"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router.add_api_route(
    path="/search-influencers",
    endpoint=search_influencers,
    methods=["POST"],
    tags=["Company"],
)

router.add_api_route(
    path="/{user_id}/approved-campaign",
    endpoint=CompaignwithAdminApprovedInfluencersById,
    methods=["GET"],
    tags=["Company"],
)

router.add_api_route(
    path="/review-pending-influencers/{campaign_id}",
    endpoint=ReviewPendingInfluencersByCampaignId,
    methods=["GET"],
    tags=["Company"],
)
router.add_api_route(
    path="/campaigns/update-influencer-status",
    endpoint=companyApprovedSingleInfluencer,
    methods=["PATCH"],
    tags=["Company"],
)


# PROFILE ROUTES
router.add_api_route(
    path="/update-profile/{user_id}",
    endpoint=update_user_profile,
    methods=["PATCH"],
    tags=["User"],
)

router.add_api_route(
    path="/user-profile/{user_id}",
    endpoint=get_user_profile,
    methods=["GET"],
    tags=["User"],
)

router.add_api_route(
    path="/change-password",
    endpoint=change_password,
    methods=["PUT"],
    tags=["User"],
)
router.add_api_route(
    path="/reset-password",
    endpoint=reset_password,
    methods=["PUT"],
    tags=["User"],
)

router.add_api_route(
    path="/send-message-to-user",
    endpoint=send_message_from_ishout_to_user,
    methods=["POST"],
    tags=["Company"],
)


@router.post("/campaign-brief", response_model=CampaignBriefResponse, tags=["Company"])
async def create_campaign_brief_endpoint(request: CampaignBriefRequest):
    return await create_campaign_brief(
        user_input=request.user_input, user_id=request.user_id
    )


@router.patch(
    "/update-campaign-brief/{brief_id}",
    response_model=CampaignBriefResponse,
    tags=["Company"],
)
async def update_campaign_brief(
    brief_id: str = Path(..., description="ID of the campaign brief to update"),
    request: UpdateCampaignBriefRequest = None,
):
    return await update_campaign_brief_service(brief_id, request)


@router.get(
    "/campaign-brief/{user_id}",
    response_model=List[CampaignBriefDBResponse],
    tags=["Company"],
)
async def get_campaign_briefs_endpoint(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
):
    return await get_campaign_briefs(user_id, skip, limit)


@router.get(
    "/campaign-brief/detail/{id}",
    response_model=CampaignBriefDBResponse,
    tags=["Company"],
)
async def get_campaign_brief_detail_endpoint(id: str):
    """
    Fetch a single campaign brief by its unique ID.
    No user_id required.
    """
    return await get_campaign_brief_by_id(id)
