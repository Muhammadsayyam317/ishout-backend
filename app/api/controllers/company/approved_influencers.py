from typing import Any, Dict, List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from app.core.exception import BadRequestException, InternalServerErrorException
from app.db.connection import get_db
from app.Schemas.campaign_influencers import (
    CampaignInfluencerStatus,
    CampaignInfluencersRequest,
)
from app.utils.helpers import convert_objectid
from app.config.credentials_config import config


async def get_company_campaign_influencers(
    campaign_id: str,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """Paginated rows from campaign_influencers for this campaign."""
    if not campaign_id:
        raise BadRequestException(message="campaign_id is required")
    if page < 1 or page_size < 1:
        raise BadRequestException(message="Invalid pagination parameters")

    try:
        campaign_oid = ObjectId(campaign_id)
    except InvalidId:
        raise BadRequestException(message="Invalid campaign_id format")

    try:
        db = get_db()
        coll = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)
        query = {"campaign_id": campaign_oid}
        skip = (page - 1) * page_size

        cursor = (
            coll.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        docs: List[Dict[str, Any]] = await cursor.to_list(length=page_size)
        influencers = [convert_objectid(dict(d)) for d in docs]
        total = await coll.count_documents(query)
        total_pages = (total + page_size - 1) // page_size if total else 0

        return {
            "campaign_id": campaign_id,
            "influencers": influencers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages if total_pages else False,
            "has_prev": page > 1,
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error fetching campaign influencers: {str(e)}"
        ) from e


async def ReviewPendingInfluencersByCampaignId(
    campaign_id: str,
    page: int = 1,
    page_size: int = 10,
):
    try:
        db = get_db()
        collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )
        cursor = collection.find(
            {
                "campaign_id": ObjectId(campaign_id),
                "status": CampaignInfluencerStatus.APPROVED.value,
                "company_approved": False,
            }
        )
        influencers = await cursor.to_list(length=None)
        influencers = [convert_objectid(doc) for doc in influencers]
        total = await collection.count_documents(
            {
                "campaign_id": ObjectId(campaign_id),
                "company_approved": False,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        )
        total_pages = (total + page_size - 1) // page_size
        return {
            "influencers": influencers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def InfluencerApprovedByCompany(
    request_data: CampaignInfluencersRequest,
):
    try:
        db = get_db()
        collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )
        existing = await collection.find_one(
            {
                "campaign_id": ObjectId(request_data.campaign_id),
                "influencer_id": ObjectId(request_data.influencer_id),
                "platform": request_data.platform,
            }
        )
        update_fields = {
            "status": request_data.status.value,
            "company_approved": True,
        }
        if existing:
            await collection.update_one(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                },
                {"$set": update_fields},
            )
        else:
            update_fields.update(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                    "admin_approved": False,
                }
            )
            await collection.insert_one(update_fields)

        return {"message": "Influencer status update successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error approving influencer: {str(e)}"
        )
