from typing import Dict, Any, List
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from app.models.campaign_model import CreateCampaignRequest, CampaignStatus
from app.db.connection import get_db


async def create_campaign(request_data: CreateCampaignRequest) -> Dict[str, Any]:
    """Create a new campaign"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign_name = request_data.name
        if not campaign_name:
            campaign_name = f"Campaign - {', '.join(request_data.category)} - {', '.join(request_data.platform)}"

        campaign_doc = {
            "name": campaign_name,
            "description": request_data.description,
            "platform": request_data.platform,
            "category": request_data.category,
            "followers": request_data.followers,
            "country": request_data.country,
            "influencer_ids": request_data.influencer_ids,  # Legacy field
            "influencer_references": [],  # New field with platform info
            "rejected_ids": [],  # Rejected by admin
            "rejectedByUser": [],  # Rejected by user
            "user_id": request_data.user_id,  # Associate with user
            "status": CampaignStatus.PENDING,  # Initial status
            "limit": request_data.limit or 10,  # Store limit for influencer generation
            "created_at": datetime.now(datetime.UTC),
            "updated_at": datetime.now(datetime.UTC),
        }

        # Insert into campaigns collection
        result = await campaigns_collection.insert_one(campaign_doc)

        return {
            "campaign_id": str(result.inserted_id),
            "message": "Campaign created successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in creating campaign: {str(e)}"
        ) from e


async def add_rejected_influencers(
    campaign_id: str, rejected_ids: List[str]
) -> Dict[str, Any]:
    """Append rejected influencer IDs to the campaign and update timestamp"""
    try:
        if not rejected_ids:
            return {"message": "No rejected ids provided"}
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        # Ensure campaign exists
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        existing_rejected: List[str] = campaign.get("rejected_ids", []) or []
        # Deduplicate while preserving order (new first then existing)
        combined = list(dict.fromkeys(existing_rejected + rejected_ids))

        result = await campaigns_collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "rejected_ids": combined,
                    "updated_at": datetime.now(datetime.UTC),
                }
            },
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500, detail="Failed to update campaign with rejected ids"
            )

        return {
            "message": "Rejected influencers recorded",
            "total_rejected": len(combined),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in add rejected influencers: {str(e)}"
        ) from e
