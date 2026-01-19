from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.db.connection import get_db
from app.Schemas.campaign import CampaignStatus
from app.utils.helpers import convert_objectid


def _get_status_message(status: str) -> str:
    status_messages = {
        "pending": "Campaign created and waiting for admin to generate influencers",
        "processing": "Admin is currently    influencers for your campaign",
        "completed": "Campaign completed with approved influencers",
    }
    return status_messages.get(status, "Unknown status")


async def all_campaigns(
    user_id: str, status: Optional[str] = None, page: int = 1, page_size: int = 10
) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        query = {"user_id": user_id}

        if status:
            query["status"] = status

        skip = (page - 1) * page_size
        total_count = await campaigns_collection.count_documents(query)
        total_pages = (total_count + page_size - 1) // page_size

        campaigns = (
            await campaigns_collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
            .to_list(length=page_size)
        )

        user_campaigns = []
        for campaign in campaigns:
            campaign = convert_objectid(campaign)
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

        return {
            "campaigns": user_campaigns,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def CompaignwithAdminApprovedInfluencersById(
    user_id: str, page: int = 1, page_size: int = 10
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")

        skip = (page - 1) * page_size

        pipeline = [
            {"$match": {"user_id": user_id, "status": CampaignStatus.APPROVED.value}},
            {"$sort": {"updated_at": -1}},
            {
                "$lookup": {
                    "from": "campaign_influencers",
                    "let": {"camp_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$campaign_id", "$$camp_id"]},
                                "company_approved": False,
                            }
                        },
                        {"$count": "pending_count"},
                    ],
                    "as": "pending_info",
                }
            },
            {
                "$addFields": {
                    "pending_influencers_count": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$pending_info.pending_count", 0]},
                            0,
                        ]
                    }
                }
            },
            {"$project": {"pending_info": 0}},
            {"$skip": skip},
            {"$limit": page_size},
        ]

        campaigns = await campaigns_collection.aggregate(pipeline).to_list(length=None)

        total = await campaigns_collection.count_documents(
            {"user_id": user_id, "status": CampaignStatus.APPROVED.value}
        )

        return {
            "campaigns": [convert_objectid(c) for c in campaigns],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
