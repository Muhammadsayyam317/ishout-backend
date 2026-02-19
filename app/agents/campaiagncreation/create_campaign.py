from agents import Runner, Agent
from agents.exceptions import InputGuardrailTripwireTriggered

from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from app.utils.prompts import CREATECAMPAIGNBREAKDOWN_PROMPT


async def create_campaign_breif(user_input: str):
    try:
        result = await Runner.run(
            Agent(
                name="create_campaign",
                instructions=CREATECAMPAIGNBREAKDOWN_PROMPT,
                input_guardrails=[CampaignCreationInputGuardrail],
                output_guardrails=[CampaignCreationOutputGuardrail],
                output_type=GenerateReplyOutput,
            ),
            input=user_input,
        )
        print("Result", result.final_output)
        return result.final_output

    except InputGuardrailTripwireTriggered as e:
        return e.fallback or "Something went wrong while creating the campaign."
