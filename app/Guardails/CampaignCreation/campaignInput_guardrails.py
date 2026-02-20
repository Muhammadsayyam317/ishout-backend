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

Your job is ONLY to block content that violates platform policies.

Block the message ONLY if it contains:
- Hate speech
- Harassment
- Sexual content involving minors
- Explicit sexual content
- Violence or illegal activities
- Fraud, scams, or impersonation
- Self-harm content
- Malicious or harmful instructions

DO NOT block:
- Any brand name
- Any campaign request
- Any influencer marketing request
- Any normal business inquiry

If the message is safe and business-related, allow it.

If it must be blocked, return a clear reason.
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
