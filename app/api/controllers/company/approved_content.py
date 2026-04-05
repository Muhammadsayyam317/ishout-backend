from typing import Any, Dict, List

from fastapi import HTTPException

from app.config.credentials_config import config
from app.db.connection import get_db
from app.utils.helpers import convert_objectid


async def get_approved_content_by_campaign_id(campaign_id: str) -> Dict[str, Any]:
    """
    Return approved-content docs for a single campaign.

    Only include docs where:
    - video_approve_admin == "approved"
    - video_approve_brand == "approved"
    """
    try:
        campaign = (campaign_id or "").strip()
        if not campaign:
            raise HTTPException(status_code=400, detail="campaign_id is required")

        db = get_db()
        approved_collection = db.get_collection(config.MONGODB_APPROVED_CONTENT)

        query = {
            "campaign_id": campaign,
            "video_approve_admin": "approved",
            "video_approve_brand": "approved",
        }

        approved_docs = await approved_collection.find(query).to_list(length=None)
        approved_docs = [convert_objectid(d) for d in approved_docs]

        return {
            "approved_contents": approved_docs,
            "total": len(approved_docs),
            "campaign_id": campaign,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in get_approved_content_by_campaign_id: {str(e)}",
        ) from e
