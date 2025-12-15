from typing import Dict, Any
from datetime import datetime, timezone
from app.models.campaign_model import CampaignStatus
from app.db.connection import get_db
from app.models.whatsappconversation_model import ConversationState
from app.utils.helpers import normalize_phone


async def create_whatsapp_campaign(state: ConversationState) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        users_collection = db.get_collection("users")

        sender_id = state.get("sender_id")
        if not sender_id:
            return {"error": "Sender ID missing", "success": False}

        phone = normalize_phone(sender_id)
        user = await users_collection.find_one({"phone": phone})
        if not user:
            return {"error": "User not found", "success": False}

        categories = state.get("category") or []
        platforms = state.get("platform") or []

        category_str = ", ".join(categories) if categories else "General"
        platform_str = ", ".join(platforms) if platforms else "General"
        campaign_name = f"Campaign - {category_str} - {platform_str}"

        campaign_doc = {
            "name": campaign_name,
            "platform": platforms,
            "category": categories,
            "followers": state.get("followers"),
            "country": state.get("country"),
            "user_id": str(user["_id"]),
            "company_name": user.get("company_name"),
            "user_type": "whatsapp",
            "status": CampaignStatus.PENDING,
            "limit": state.get("limit"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await campaigns_collection.insert_one(campaign_doc)
        print("✅ Campaign inserted with ID:", result.inserted_id)

        return {
            "campaign_id": str(result.inserted_id),
            "success": True,
        }

    except Exception as e:
        return {
            "error": f"Error creating campaign: {str(e)}",
            "success": False,
        }
