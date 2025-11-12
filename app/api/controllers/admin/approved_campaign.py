from fastapi import Depends, HTTPException

from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access
from app.models.campaign_model import CampaignStatus


async def approved_campaign(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(require_admin_access),
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")

        status_value = CampaignStatus.COMPLETED
        query = {"status": status_value}

        # Only fetch fields we need to compute counts and metadata
        projection = {
            "name": 1,
            "description": 1,
            "platform": 1,
            "category": 1,
            "followers": 1,
            "country": 1,
            "influencer_ids": 1,
            "rejected_ids": 1,
            "rejectedByUser": 1,
            "generated_influencers": 1,
            "user_id": 1,
            "status": 1,
            "limit": 1,
            "created_at": 1,
            "updated_at": 1,
        }

        total = await campaigns_collection.count_documents(query)
        cursor = (
            campaigns_collection.find(query, projection)
            .sort("created_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=None)

        formatted = []
        for doc in docs:
            influencer_ids = doc.get("influencer_ids", []) or []
            rejected_ids = doc.get("rejected_ids", []) or []
            rejected_by_user = doc.get("rejectedByUser", []) or []
            generated = doc.get("generated_influencers", []) or []

            formatted.append(
                {
                    "campaign_id": str(doc.get("_id")),
                    "name": doc.get("name"),
                    "platform": doc.get("platform"),
                    "category": doc.get("category"),
                    "followers": doc.get("followers"),
                    "country": doc.get("country"),
                    "user_id": str(doc.get("user_id")) if doc.get("user_id") else None,
                    "status": doc.get("status"),
                    "limit": doc.get("limit"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                    "total_approved": len(influencer_ids),
                    "total_rejected": len(rejected_ids),
                    "total_rejected_by_user": len(rejected_by_user),
                    "total_generated": len(generated),
                }
            )

        total_pages = total + page_size - 1

        return {
            "campaigns": formatted,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in approved campaign: {str(e)}"
        ) from e
