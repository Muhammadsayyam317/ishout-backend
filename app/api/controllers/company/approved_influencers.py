from fastapi import Depends, HTTPException

from app.db.connection import get_db
from app.models.campaign_model import CampaignStatus
from app.utils.helpers import convert_objectid


async def get_company_approved_influencers(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
):
    try:
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="Invalid pagination parameters")
        db = get_db()
        influencers_collection = db.get_collection("campaigns")
        query = {
            "user_id": user_id,
            "status": CampaignStatus.APPROVED.value,
        }

        skip = (page - 1) * page_size

        cursor = (
            influencers_collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(page_size)
        )

        influencers = await cursor.to_list(length=page_size)
        cleaned = [convert_objectid(influencer) for influencer in influencers]

        total = await influencers_collection.count_documents(query)
        total_pages = (total + page_size - 1) // page_size

        return {
            "approved_influencers": cleaned,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
