from typing import Any, Dict
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access


async def delete_campaign_ById(
    campaign_id: str,
    current_user: dict = Depends(require_admin_access),
) -> Dict[str, Any]:
    """Delete a campaign (admin only)"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        result = await campaigns_collection.delete_one({"_id": ObjectId(campaign_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in delete campaign: {str(e)}"
        ) from e
