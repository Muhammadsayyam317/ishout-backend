from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.api.controllers.influencers_controller import find_influencers
from app.api.controllers.twilio_controller import send_message
from app.models.influencers_model import FindInfluencerRequest

router = APIRouter()

@router.get("/")
def test_route():
    """Simple test endpoint"""
    return {"message": "Test Route"}

@router.post("/find-influencer")
async def find_influencer_route(request_data: List[FindInfluencerRequest]):
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