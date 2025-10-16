from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.api.controllers.influencers_controller import find_influencers
from app.api.controllers.twilio_controller import send_message
from app.models.influencers_model import FindInfluencerRequest, DeleteInfluencerRequest
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