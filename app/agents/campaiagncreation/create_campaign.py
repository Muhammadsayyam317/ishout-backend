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


async def create_campaign_brief(user_input: str):
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

        campaign_data = result.final_output
        if not isinstance(campaign_data, dict):
            return {
                "error": "Invalid response format from AI. Expected structured JSON."
            }

        return campaign_data

    except InputGuardrailTripwireTriggered as e:
        return {"error": "Input validation triggered.", "details": str(e)}

    except Exception as e:
        return {
            "error": "Something went wrong while creating the campaign.",
            "details": str(e),
        }
