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
import json


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

        raw_output = result.final_output
        if isinstance(raw_output, dict):
            campaign_json = raw_output
        else:
            campaign_json = json.loads(raw_output)

        print("Campaign JSON:", campaign_json)
        return campaign_json

    except InputGuardrailTripwireTriggered as e:
        print("Input guardrail triggered:", str(e))
        return {"error": "Input validation triggered."}

    except json.JSONDecodeError as e:
        print("JSON parsing error:", str(e))
        return {"error": "Failed to parse JSON from agent output."}

    except Exception as e:
        print("Unexpected error:", str(e))
        return {"error": "Something went wrong while creating the campaign."}
