from typing import List, Dict, Any
from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from datetime import datetime


def serialize_influencer(inf: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ObjectId and datetime fields to JSON-serializable types."""
    return {
        **inf,
        "_id": str(inf["_id"]),
        "campaign_id": str(inf["campaign_id"]),
        "created_at": (
            inf["created_at"].isoformat()
            if isinstance(inf.get("created_at"), datetime)
            else inf.get("created_at")
        ),
        "updated_at": (
            inf["updated_at"].isoformat()
            if isinstance(inf.get("updated_at"), datetime)
            else inf.get("updated_at")
        ),
    }


async def get_generated_influencers(campaign_id: str) -> List[Dict[str, Any]]:
    try:
        db = get_db()
        collection = db.get_collection("generated_influencers")
        influencers = await collection.find(
            {"campaign_id": ObjectId(campaign_id)}
        ).to_list(length=100)
        return [serialize_influencer(inf) for inf in influencers]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in get generated influencers: {str(e)}"
        ) from e
