from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

from app.Schemas.instagram.message_schema import InputGuardrailResult


@input_guardrail(name="CampaignCreationInputGuardrail")
async def CampaignCreationInputGuardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    message: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        Agent(
            name="campaign_creation_input_guardrail",
            instructions="""
You are a safety and compliance guardrail for campaign creation.
iShout is a platform for managing social media campaigns and providing influncers to the brand for their campaigns in multiple platforms.
You must block the message if it contains any of the following:
anything violet listed below:
- The message is not a brand name
- The brand name is not valid
- The brand name is not found in the company website
- If the message is not allowed, you must return the reason why it is not allowed.
""",
            output_type=InputGuardrailResult,
        ),
        input=message,
        context=context,
    )
    print("🛡️ Campaign Creation Input Guardrail result:", result.final_output)
    if not result.final_output.allowed:
        return GuardrailFunctionOutput(
            output_info=result.final_output.reason,
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(
        output_info=None,
        tripwire_triggered=False,
    )


@input_guardrail(name="WhatsappInputGuardrail")
async def WhatsappInputGuardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    message: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    return GuardrailFunctionOutput(
        output_info=None,
        tripwire_triggered=False,
    )
