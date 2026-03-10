from typing import Any, Dict
from bson import ObjectId
from fastapi import Depends

from app.core.exception import InternalServerErrorException, NotFoundException
from app.db.connection import get_db
from app.middleware.auth_middleware import require_admin_access


async def delete_campaign_ById(
    campaign_id: str,
    current_user: dict = Depends(require_admin_access),
) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        generated_collection = db.get_collection("generated_influencers")
        campaign_influencers_collection = db.get_collection("campaign_influencers")
        briefs_collection = db.get_collection("CampaignBriefGeneration")

        # First, fetch the campaign so we can see if it has an attached brief_id.
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(campaign_id)}
        )
        if not campaign:
            raise NotFoundException(message="Campaign not found")

        brief_id = campaign.get("brief_id")

        # Delete the campaign itself.
        result = await campaigns_collection.delete_one({"_id": ObjectId(campaign_id)})

        # Delete generated influencers and campaign influencers for this campaign.
        generated_result = await generated_collection.delete_many(
            {"campaign_id": ObjectId(campaign_id)}
        )
        campaign_influencers_result = await campaign_influencers_collection.delete_many(
            {"campaign_id": ObjectId(campaign_id)}
        )

        # If the campaign had an associated brief, delete that brief record as well.
        if brief_id:
            await briefs_collection.delete_one({"_id": str(brief_id)})

        if result.deleted_count == 0:
            raise NotFoundException(message="Campaign not found")
        if generated_result.deleted_count == 0:
            raise NotFoundException(message="Generated influencers not found")
        if campaign_influencers_result.deleted_count == 0:
            raise NotFoundException(message="Campaign influencers not found")
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in delete campaign: {str(e)}"
        ) from e
