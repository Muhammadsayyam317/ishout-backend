from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.api.controllers.influencers_controller import find_influencers, more_influencers
from app.api.controllers.campaign_controller import create_campaign, get_all_campaigns, get_campaign_by_id, approve_single_influencer
from app.api.controllers.twilio_controller import send_message
from app.models.influencers_model import FindInfluencerRequest, DeleteInfluencerRequest, MoreInfluencerRequest
from app.models.campaign_model import CreateCampaignRequest, ApproveSingleInfluencerRequest
from app.services.embedding_service import delete_from_vector_store

router = APIRouter()

@router.get("/")
def test_route():
    """Simple test endpoint"""
    return {"message": "Test Route"}

@router.post("/find-influencer")
async def find_influencer_route(request_data: FindInfluencerRequest):
    """Endpoint to find influencers based on provided criteria"""
    try:
        return await find_influencers(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-influencer/more")
async def more_influencer_route(request_data: MoreInfluencerRequest):
    """Get a fresh batch of influencers excluding provided IDs."""
    try:
        return await more_influencers(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp")
async def create_message_route(request_data: Dict[str, Any]):
    """Endpoint for Twilio WhatsApp integration"""
    try:
        message_sid = await send_message(request_data)
        return {"message_sid": message_sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-influencer")
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


# Campaign endpoints
@router.post("/campaigns")
async def create_campaign_route(request_data: CreateCampaignRequest):
    """Create a new campaign"""
    try:
        return await create_campaign(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns")
async def get_campaigns_route():
    """Get all campaigns"""
    try:
        return await get_all_campaigns()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}")
async def get_campaign_route(campaign_id: str):
    """Get campaign details by ID with populated influencer data"""
    try:
        return await get_campaign_by_id(campaign_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaigns/approve-single-influencer")
async def approve_single_influencer_route(request_data: ApproveSingleInfluencerRequest):
    """Approve a single influencer and add to campaign"""
    try:
        return await approve_single_influencer(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))