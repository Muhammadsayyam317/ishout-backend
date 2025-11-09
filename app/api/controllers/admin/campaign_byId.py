from app.db.connection import get_db
from bson import ObjectId
from fastapi import Depends, HTTPException
from app.middleware.auth_middleware import require_admin_access


async def campaign_by_id_controller(
    campaign_id: str,
    current_user: dict = Depends(require_admin_access),
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        campaign["_id"] = str(campaign["_id"])
        return campaign

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
