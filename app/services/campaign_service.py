from typing import Dict, Any
from fastapi import HTTPException
from app.models.campaign_model import CampaignStatus
from app.db.connection import get_db
from app.models.whatsappconversation_model import ConversationState
from datetime import datetime, timezone


async def create_whatsapp_campaign(state: ConversationState) -> Dict[str, Any]:
    """Create a new campaign for whatsapp user"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")

        categories = state.get("category") or []
        platforms = state.get("platform") or []

        category_str = (
            ", ".join(categories) if isinstance(categories, list) else str(categories)
        )
        platform_str = (
            ", ".join(platforms) if isinstance(platforms, list) else str(platforms)
        )

        campaign_name = f"Campaign - {category_str} - {platform_str}"

        campaign_doc = {
            "name": campaign_name,
            "platform": state.get("platform"),
            "category": state.get("category"),
            "followers": state.get("followers"),
            "country": state.get("country"),
            "user_id": state.get("sender_id"),
            "user_type": "whatsapp",
            "status": CampaignStatus.PENDING,
            "limit": state.get("limit"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await campaigns_collection.insert_one(campaign_doc)

        return {
            "message": (
                "Thank you! I have received all your campaign details. "
                "Once our admin reviews your request, we will share the matching influencers with you."
            ),
            "campaign_id": str(result.inserted_id),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in creating campaign: {str(e)}"
        ) from e


# async def add_rejected_influencers(
#     campaign_id: str, rejected_ids: List[str]
# ) -> Dict[str, Any]:
#     """Append rejected influencer IDs to the campaign and update timestamp"""
#     try:
#         if not rejected_ids:
#             return {"message": "No rejected ids provided"}
#         db = get_db()
#         campaigns_collection = db.get_collection("campaigns")
#         # Ensure campaign exists
#         campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
#         if not campaign:
#             raise HTTPException(status_code=404, detail="Campaign not found")

#         existing_rejected: List[str] = campaign.get("rejected_ids", []) or []
#         # Deduplicate while preserving order (new first then existing)
#         combined = list(dict.fromkeys(existing_rejected + rejected_ids))

#         result = await campaigns_collection.update_one(
#             {"_id": ObjectId(campaign_id)},
#             {
#                 "$set": {
#                     "rejected_ids": combined,
#                     "updated_at": datetime.now(datetime.UTC),
#                 }
#             },
#         )

#         if result.modified_count == 0:
#             raise HTTPException(
#                 status_code=500, detail="Failed to update campaign with rejected ids"
#             )

#         return {
#             "message": "Rejected influencers recorded",
#             "total_rejected": len(combined),
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error in add rejected influencers: {str(e)}"
#         ) from e
