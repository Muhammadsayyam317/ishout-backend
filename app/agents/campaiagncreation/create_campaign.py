from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from agents import Runner, Agent
from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from typing import Dict
from app.Schemas.campaign_influencers import (
    CampaignBriefDBResponse,
    CampaignBriefResponse,
    UpdateCampaignBriefRequest,
)
from app.model.Campaign.campaignbrief_model import (
    CampaignBriefGeneration,
    CampaignBriefStatus,
)
from app.utils.prompts import CREATECAMPAIGNBREAKDOWN_PROMPT
from app.db.connection import get_db
from agents.exceptions import InputGuardrailTripwireTriggered
import json


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


async def create_campaign_brief(user_input: str, user_id: str) -> CampaignBriefResponse:
    user_doc = await validate_user(user_id)

    try:
        result = await Runner.run(
            Agent(
                name="create_campaign",
                instructions=CREATECAMPAIGNBREAKDOWN_PROMPT,
                input_guardrails=[CampaignCreationInputGuardrail],
                output_guardrails=[CampaignCreationOutputGuardrail],
                output_type=CampaignBriefResponse,
            ),
            input=user_input,
        )

        if isinstance(result.final_output, dict):
            response_obj = CampaignBriefResponse(**result.final_output)
        elif isinstance(result.final_output, CampaignBriefResponse):
            response_obj = result.final_output
        else:
            response_obj = CampaignBriefResponse(**json.loads(result.final_output))

        stored_doc = await store_campaign_brief(
            prompt=user_input,
            response=response_obj,
            user_doc=user_doc,
        )

        response_obj.id = stored_doc.id
        return response_obj

    except InputGuardrailTripwireTriggered:
        raise HTTPException(status_code=400, detail="Invalid campaign request.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Campaign generation failed: {str(e)}"
        )


async def update_campaign_brief_service(
    brief_id: str, update_request: UpdateCampaignBriefRequest
) -> CampaignBriefResponse:

    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    existing_brief = await collection.find_one({"_id": brief_id})
    if not existing_brief:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    update_data = {k: v for k, v in update_request.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    await collection.update_one(
        {"_id": brief_id},
        {"$set": {f"response.{k}": v for k, v in update_data.items()}},
    )

    updated_brief = await collection.find_one({"_id": brief_id})
    response_obj = CampaignBriefResponse(**updated_brief["response"])
    response_obj.id = str(updated_brief["_id"])

    return response_obj


async def get_campaign_briefs(
    user_id: str, skip: int = 0, limit: int = 10
) -> List[CampaignBriefDBResponse]:

    user_doc = await validate_user(user_id)
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    cursor = (
        collection.find({"user_id": str(user_doc["_id"])})
        .sort("version", -1)
        .skip(skip)
        .limit(limit)
    )

    briefs = []

    async for doc in cursor:
        response_data = doc.get("response", {})
        if "title" not in response_data or not response_data.get("title"):
            response_data["title"] = "Untitled Campaign"

        try:
            response_obj = CampaignBriefResponse(**response_data)
        except Exception as e:
            print(f"CampaignBrief parsing error: {e}")
            continue

        briefs.append(
            CampaignBriefDBResponse(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                prompt=doc["prompt"],
                response=response_obj,
                status=doc["status"],
                version=doc["version"],
                regenerated_from=doc.get("regenerated_from"),
                created_at=doc.get("created_at"),
            )
        )

    return briefs


async def get_campaign_brief_by_id(campaign_id: str):
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    campaign = await collection.find_one({"_id": campaign_id})

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    response_data = campaign.get("response", {})
    if "title" not in response_data or not response_data.get("title"):
        response_data["title"] = "Untitled Campaign"

    try:
        response_obj = CampaignBriefResponse(**response_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Corrupted campaign brief data: {str(e)}"
        )

    return CampaignBriefDBResponse(
        id=str(campaign["_id"]),
        user_id=campaign["user_id"],
        prompt=campaign["prompt"],
        response=response_obj,
        status=campaign["status"],
        version=campaign["version"],
        regenerated_from=campaign.get("regenerated_from"),
        created_at=campaign.get("created_at"),
    )
