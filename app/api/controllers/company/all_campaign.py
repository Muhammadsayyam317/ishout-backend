from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.db.connection import get_db


def _get_status_message(status: str) -> str:
    status_messages = {
        "pending": "Campaign created and waiting for admin to generate influencers",
        "processing": "Admin is currently generating influencers for your campaign",
        "completed": "Campaign completed with approved influencers",
    }
    return status_messages.get(status, "Unknown status")


async def all_campaigns(user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        query = {"user_id": user_id}
        if status:
            query["status"] = status

        campaigns = (
            await campaigns_collection.find(query).sort("created_at", -1).to_list(None)
        )

        user_campaigns = []
        for campaign in campaigns:
            campaign_dict = {
                "campaign_id": str(campaign["_id"]),
                "name": campaign["name"],
                "platform": campaign["platform"],
                "category": campaign["category"],
                "followers": campaign["followers"],
                "country": campaign["country"],
                "limit": campaign["limit"],
                "status": campaign.get("status", "pending"),
                "status_message": _get_status_message(
                    campaign.get("status", "pending")
                ),
                "created_at": campaign["created_at"],
                "updated_at": campaign["updated_at"],
            }

            user_campaigns.append(campaign_dict)

        return {"campaigns": user_campaigns, "total": len(user_campaigns)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
