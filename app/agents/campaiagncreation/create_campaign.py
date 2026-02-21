import json
from fastapi import HTTPException
from agents import Runner, Agent
from agents.exceptions import InputGuardrailTripwireTriggered

from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from app.Schemas.campaign_influencers import CampaignBriefResponse
from app.utils.prompts import CREATECAMPAIGNBREAKDOWN_PROMPT


async def create_campaign_brief(user_input: str) -> CampaignBriefResponse:
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
        return result.final_output
    except InputGuardrailTripwireTriggered as e:
        raise HTTPException(
            status_code=400, detail=f"Input validation triggered: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")
