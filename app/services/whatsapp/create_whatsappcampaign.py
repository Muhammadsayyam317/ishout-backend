from typing import Dict, Any
from fastapi import HTTPException
from app.models.campaign_model import CampaignStatus
from app.db.connection import get_db
from app.models.whatsappconversation_model import ConversationState
from datetime import datetime, timezone


async def create_whatsapp_campaign(state: ConversationState) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        whatsapp_users_collection = db.get_collection("whatsapp_users")

        categories = state.get("category") or []
        platforms = state.get("platform") or []

        category_str = (
            ", ".join(categories) if isinstance(categories, list) else str(categories)
        )
        platform_str = (
            ", ".join(platforms) if isinstance(platforms, list) else str(platforms)
        )

        campaign_name = f"Campaign - {category_str} - {platform_str}"
        company_name = state.get("name")
        if not company_name:
            sender_id = state.get("sender_id")
            if sender_id:
                whatsapp_user = await whatsapp_users_collection.find_one(
                    {"sender_id": sender_id}
                )
                if whatsapp_user:
                    company_name = whatsapp_user.get("name")

        campaign_doc = {
            "name": campaign_name,
            "platform": state.get("platform"),
            "category": state.get("category"),
            "followers": state.get("followers"),
            "country": state.get("country"),
            "user_id": state.get("sender_id"),
            "company_name": company_name,
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
