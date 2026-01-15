from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
    AgentOutputSchema,
)


class OutputGuardrailInput(BaseModel):
    input: str
    output: str


class OutputGuardrailResult(BaseModel):
    allowed: bool
    reason: str | None = None
    escalate: bool = False
    fallback: str | None = None
    output_info: str | None = None
    tripwire_triggered: bool | None = None


guardrail_agent = Agent(
    name="output_guardrail",
    instructions="""
You review Instagram DM replies before sending.

Block outputs that:
- Sound robotic or repetitive
- Contain pricing outside allowed ranges
- Accept or confirm a deal
- Mention contracts, payments, or legal steps
- Reference AI, automation, or internal rules

If blocked:
- Provide a natural human fallback (1–2 lines)
""",
    output_type=AgentOutputSchema(OutputGuardrailResult, strict_json_schema=False),
)


@output_guardrail(name="InstagramOutputGuardrail")
async def InstagramOutputGuardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: OutputGuardrailInput,
) -> GuardrailFunctionOutput:
    """
    Evaluates an Instagram DM reply and applies guardrails.

    Returns a GuardrailFunctionOutput indicating if the message is allowed,
    with optional escalation and fallback information.
    """

    result = await Runner.run(
        guardrail_agent,
        input=input,
        context=ctx,
    )

    guardrail_output: OutputGuardrailResult = result.final_output
    return GuardrailFunctionOutput(
        allowed=guardrail_output.allowed,
        reason=guardrail_output.reason,
        escalate=guardrail_output.escalate,
        fallback=guardrail_output.fallback,
        output_info=guardrail_output.output_info,
        tripwire_triggered=guardrail_output.tripwire_triggered,
    )
