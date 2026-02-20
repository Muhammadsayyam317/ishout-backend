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
            ),
            input=user_input,
        )

        output = result.final_output
        if isinstance(output, dict):
            return CampaignBriefResponse(**output)

        if isinstance(output, str):
            parsed = json.loads(output)
            return CampaignBriefResponse(**parsed)

        raise HTTPException(status_code=500, detail="Unexpected AI response format.")

    except InputGuardrailTripwireTriggered as e:
        raise HTTPException(
            status_code=400, detail=f"Input validation triggered: {str(e)}"
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON format.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")
