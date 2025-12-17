from typing import Dict, Any
from datetime import datetime, timezone
from app.models.campaign_model import CampaignStatus
from app.db.connection import get_db
from app.models.whatsappconversation_model import ConversationState
from app.utils.helpers import normalize_phone


async def create_whatsapp_campaign(state: ConversationState) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns = db.get_collection("campaigns")
        users = db.get_collection("users")

        sender_id = state.get("sender_id")
        if not sender_id:
            return {"success": False, "error": "Sender ID missing"}

        phone = normalize_phone(sender_id)
        if not phone:
            return {"success": False, "error": "Invalid phone number"}

        user = await users.find_one({"phone": phone})
        if not user:
            return {"success": False, "error": "User not found"}

        categories = list(map(str, state.get("category") or []))
        platforms = list(map(str, state.get("platform") or []))
        followers = list(map(str, state.get("followers") or []))
        country = list(map(str, state.get("country") or []))

        campaign_name = (
            f"Campaign - {', '.join(categories or ['General'])} - "
            f"{', '.join(platforms or ['General'])}"
        )

        campaign_doc = {
            "name": campaign_name,
            "platform": platforms,
            "category": categories,
            "followers": followers,
            "country": country,
            "user_id": str(user["_id"]),
            "whatsapp_phone": phone,
            "company_name": user.get("company_name"),
            "user_type": "whatsapp",
            "status": CampaignStatus.PENDING,
            "limit": int(state.get("limit") or 1),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await campaigns.insert_one(campaign_doc)

        return {"success": True, "campaign_id": str(result.inserted_id)}

    except Exception as e:
        return {"success": False, "error": str(e)}
