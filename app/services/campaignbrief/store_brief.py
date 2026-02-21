from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from app.Schemas.campaign_influencers import CampaignBriefResponse
from app.model.Campaign.campaignbrief_model import (
    CampaignBriefGeneration,
    CampaignBriefStatus,
)
from app.db.connection import get_db


async def validate_user(user_id: str):
    db = get_db()
    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def store_campaign_brief(
    prompt: str,
    response: CampaignBriefResponse,
    user_doc: dict,
    regenerated_from: Optional[str] = None,
) -> CampaignBriefGeneration:
    try:
        db = get_db()
        collection = db.get_collection("CampaignBriefGeneration")
        user_id = str(user_doc["_id"])
        last_brief = await collection.find_one(
            {"user_id": user_id}, sort=[("version", -1)]
        )
        next_version = 1 if not last_brief else last_brief.get("version", 0) + 1
        document = CampaignBriefGeneration(
            user_id=user_id,
            prompt=prompt,
            response=response,
            status=(
                CampaignBriefStatus.REGENERATED
                if regenerated_from
                else CampaignBriefStatus.GENERATED
            ),
            version=next_version,
            regenerated_from=regenerated_from,
        )
        await collection.insert_one(document.model_dump(by_alias=True))
        return document

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to store campaign brief: {str(e)}"
        )


async def CampaignBriefById(user_id: str) -> CampaignBriefResponse:
    try:
        db = get_db()
        collection = db.get_collection("CampaignBriefGeneration")
        result = await collection.find_one({"user_id": user_id}, sort=[("version", -1)])
        if not result:
            raise HTTPException(status_code=404, detail="Campaign brief not found")
        return CampaignBriefResponse(**result["response"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get campaign brief: {str(e)}"
        )
