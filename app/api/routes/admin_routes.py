from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.Schemas.influencers import MoreInfluencerRequest

from app.agents.Instagram.session.instauser_session import (
    all_instagram_user_sessions,
)
from app.api.controllers.admin.campaign_controller import (
    add_influencer_Number,
    update_status,
)
from app.api.controllers.admin.delete_whatsappchat import delete_whatsapp_chat
from app.api.controllers.admin.generated_influencers import get_generated_influencers
from app.api.controllers.admin.influencers_controller import more_influencers
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
    reject_and_regenerate_influencer,
)
from app.api.controllers.admin.takeover import (
    send_human_message,
    send_admin_influencer_message,
    send_admin_company_message,
    send_company_admin_message,
    admin_approve_video_to_brand,
    takeover_value,
    toggle_human_takeover,
    toggle_negotiation_takeover,
    negotiation_takeover_value,
    update_negotiation_approval_status,
    send_negotiation_human_message,
)
from app.api.controllers.admin.user_managment import (
    Whatsapp_Users_Sessions_management,
    Whatsapp_messages_management,
    whatsapp_admin_influencer_messages_management,
    whatsapp_admin_company_messages_management,
    delete_user,
    get_all_users,
    update_user_status,
)
from app.api.controllers.company.company_data import company_data
from app.core.redis import redis_info
from app.Schemas.campaign import (
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
)
from app.middleware.auth_middleware import require_admin_access
from app.services.instagram.list_on_conversations import (
    instagram_conversation_messages,
    instagram_conversations_list,
)
from app.services.negotiation.InitialMessage import NegotiationInitialMessage
from app.services.negotiation.negotiation import (
    get_all_negotiation_controls,
    get_negotiation_control_detail,
    delete_negotiation_control,
)


router = APIRouter()


@router.post("/campaigns/generate-influencers/{campaign_id}", tags=["Admin"])
async def generate_influencers_route(
    campaign_id: str,
    request_data: AdminGenerateInfluencersRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin_access),
):
    try:
        return await admin_generate_influencers(
            campaign_id, request_data, background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


router.add_api_route(
    path="/campaigns/reject-and-regenerate",
    endpoint=reject_and_regenerate_influencer,
    methods=["POST"],
    tags=["Admin"],
)

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
    path="/delete-user/{user_id}",
    endpoint=delete_user,
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

router.add_api_route(
    path="/redis/info",
    endpoint=redis_info,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/user-management",
    endpoint=get_all_users,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/user-management/{user_id}",
    endpoint=update_user_status,
    methods=["PATCH"],
    tags=["Admin"],
)

router.add_api_route(
    path="/generated-influencers/{campaign_id}",
    endpoint=get_generated_influencers,
    methods=["GET"],
    tags=["Admin"],
)


@router.post("/more-influencers", tags=["Admin"])
async def more_influencers_route(
    request_data: MoreInfluencerRequest,
    background_tasks: BackgroundTasks,
):
    try:
        return await more_influencers(request_data, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router.add_api_route(
    path="/add-influencer-number",
    endpoint=add_influencer_Number,
    methods=["POST"],
    tags=["Admin"],
)

router.add_api_route(
    path="/whatsapp-users-sessions",
    endpoint=Whatsapp_Users_Sessions_management,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp-messages/{thread_id}",
    endpoint=Whatsapp_messages_management,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp/send-human-message/{thread_id}",
    endpoint=send_human_message,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp-admin-influencer/send-human-message/{thread_id}",
    endpoint=send_admin_influencer_message,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp-admin-influencer-messages/{thread_id}",
    endpoint=whatsapp_admin_influencer_messages_management,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp-admin-company/send-human-message/{thread_id}",
    endpoint=send_admin_company_message,
    methods=["POST"],
    tags=["Admin"],
)

router.add_api_route(
    path="/whatsapp-admin-company/send-company-admin-message/{user_id}",
    endpoint=send_company_admin_message,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp-admin-company-messages/{thread_id}",
    endpoint=whatsapp_admin_company_messages_management,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/whatsapp-admin-company/approve-video",
    endpoint=admin_approve_video_to_brand,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp/toggle-takeover/{thread_id}",
    endpoint=toggle_human_takeover,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/whatsapp/takeover-value/{thread_id}",
    endpoint=takeover_value,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/negotiation/toggle-takeover/{thread_id}",
    endpoint=toggle_negotiation_takeover,
    methods=["POST"],
    tags=["Admin"],
)
router.add_api_route(
    path="/negotiation/takeover-value/{thread_id}",
    endpoint=negotiation_takeover_value,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/negotiation/approval-status/{thread_id}",
    endpoint=update_negotiation_approval_status,
    methods=["PATCH"],
    tags=["Admin"],
)
router.add_api_route(
    path="/negotiation/send-human-message/{thread_id}",
    endpoint=send_negotiation_human_message,
    methods=["POST"],
    tags=["Admin"],
)

router.add_api_route(
    path="/instagram/conversations-list",
    endpoint=instagram_conversations_list,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/instagram/conversation-with-user",
    endpoint=instagram_conversation_messages,
    methods=["GET"],
    tags=["Admin"],
)
router.add_api_route(
    path="/instagram/instagram-user-session",
    endpoint=all_instagram_user_sessions,
    methods=["GET"],
    tags=["Admin"],
)

router.add_api_route(
    path="/delete-whatsapp-chat/{thread_id}",
    endpoint=delete_whatsapp_chat,
    methods=["DELETE"],
    tags=["Admin"],
)

router.add_api_route(
    path="/negotiation-initial-message",
    endpoint=NegotiationInitialMessage,
    methods=["POST"],
    tags=["Admin"],
)


@router.get("/negotiation-controls", tags=["Admin"])
async def negotiation_controls_route(
    page: int = 1,
    page_size: int = 10,
):
    try:
        return await get_all_negotiation_controls(page, page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/negotiation-chat-detail", tags=["Admin"])
async def negotiation_control_detail_route(_id: str):
    """
    Get a single negotiation control's key details by _id:
    - name
    - phone
    - history
    - conversation_mode
    """
    detail = await get_negotiation_control_detail(_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Negotiation control not found")
    return detail


@router.delete("/negotiation-controls/{thread_id}", tags=["Admin"])
async def delete_negotiation_control_route(
    thread_id: str,
    current_user: dict = Depends(require_admin_access),
):
    try:
        result = await delete_negotiation_control(thread_id)
        if not result:
            raise HTTPException(status_code=404, detail="Negotiation control not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
