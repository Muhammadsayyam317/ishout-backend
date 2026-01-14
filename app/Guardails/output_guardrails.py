from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
from pydantic import BaseModel
from agents import AgentOutputSchema


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
    instructions="You are a guardrail agent that checks the output message for any red flags",
    output_type=AgentOutputSchema(OutputGuardrailResult, strict_json_schema=False),
)


@output_guardrail(name="InstagramOutputGuardrail")
async def InstagramOutputGuardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: OutputGuardrailInput,
) -> GuardrailFunctionOutput:

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
