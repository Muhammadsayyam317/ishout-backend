from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)


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
    output_type=OutputGuardrailResult,
)


@output_guardrail(name="InstagramOutputGuardrail")
async def InstagramOutputGuardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: dict,
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        guardrail_agent,
        input=input,
        context=ctx,
    )
    if not result.final_output.allowed:
        return GuardrailFunctionOutput(
            output_info=result.final_output.fallback
            or "Let me quickly check this and get back to you.",
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=False,
    )
