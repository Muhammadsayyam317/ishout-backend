from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from agents import Runner, Agent
from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from app.Schemas.campaign_influencers import CampaignBriefResponse
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
