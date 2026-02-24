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
from app.Schemas.campaign_influencers import (
    CampaignBriefDBResponse,
    CampaignBriefResponse,
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
        return stored_doc.response

    except InputGuardrailTripwireTriggered:
        raise HTTPException(status_code=400, detail="Invalid campaign request.")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Campaign generation failed: {str(e)}"
        )


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
        briefs.append(
            CampaignBriefDBResponse(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                prompt=doc["prompt"],
                response=CampaignBriefResponse(**doc["response"]),
                status=doc["status"],
                version=doc["version"],
                regenerated_from=doc.get("regenerated_from"),
                created_at=doc.get("created_at"),
            )
        )

    return briefs


async def get_campaign_brief_by_id(campaign_id: str):
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")  # correct collection

    campaign = await collection.find_one({"_id": campaign_id})  # fetch only by _id

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    # Convert to response model
    return CampaignBriefDBResponse(
        id=str(campaign["_id"]),
        user_id=campaign["user_id"],
        prompt=campaign["prompt"],
        response=CampaignBriefResponse(**campaign["response"]),
        status=campaign["status"],
        version=campaign["version"],
        regenerated_from=campaign.get("regenerated_from"),
        created_at=campaign.get("created_at"),
    )