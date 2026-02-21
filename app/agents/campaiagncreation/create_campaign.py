from fastapi import HTTPException
from agents import Runner, Agent
from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from app.Schemas.campaign_influencers import CampaignBriefResponse
from app.services.campaignbrief.store_brief import store_campaign_brief, validate_user
from app.utils.prompts import CREATECAMPAIGNBREAKDOWN_PROMPT
from agents.exceptions import InputGuardrailTripwireTriggered
import json


async def create_campaign_brief(user_input: str, user_id: str) -> CampaignBriefResponse:
    user = await validate_user(user_id)
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
            response = CampaignBriefResponse(**result.final_output)
        elif isinstance(result.final_output, CampaignBriefResponse):
            response = result.final_output
        else:
            response = CampaignBriefResponse(**json.loads(result.final_output))
        stored_doc = await store_campaign_brief(
            prompt=user_input,
            response=response,
            user_doc=user,
        )
        return stored_doc.response

    except InputGuardrailTripwireTriggered:
        raise HTTPException(status_code=400, detail="Invalid campaign request.")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Campaign generation failed: {str(e)}"
        )


async def regenerate_campaign_brief(
    user_input: str, user_id: str
) -> CampaignBriefResponse:
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
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Campaign generation failed: {str(e)}"
        )
