from fastapi import APIRouter, HTTPException, Depends, Header, status
from typing import Dict, Any, Optional
from app.api.controllers.influencers_controller import find_influencers_by_campaign, more_influencers, find_influencers, more_influencers_legacy
from app.api.controllers.campaign_controller import create_campaign, get_all_campaigns, get_campaign_by_id, approve_single_influencer, approve_multiple_influencers
from app.api.controllers.twilio_controller import send_message
from app.api.controllers.auth_controller import get_current_user
from app.models.influencers_model import FindInfluencerRequest, DeleteInfluencerRequest, MoreInfluencerRequest, FindInfluencerLegacyRequest, MoreInfluencerLegacyRequest
from app.models.campaign_model import CreateCampaignRequest, ApproveSingleInfluencerRequest, ApproveMultipleInfluencersRequest
from app.services.embedding_service import delete_from_vector_store
from app.middleware.auth_middleware import get_authenticated_user, get_optional_user, require_admin_access, security

router = APIRouter()


@router.get("/")
def indexView():
    return {"message": "Hello, World!"}


@router.delete("/delete-influencer", tags=["Admin"])
async def delete_influencer_route(request: DeleteInfluencerRequest):
    """Delete influencer data and embeddings from the platform collection.

    Accepts one of: document_id (preferred), username, or url.
    """
    try:
        result = await delete_from_vector_store(
            platform=request.platform,
            influencer_id=request.influencer_id,
        )
        if result.get("deleted_count", 0) == 0:
            raise HTTPException(status_code=400, detail="No matching document found to delete")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

