from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from agents import AgentOutputSchema


class InputGuardrailResult(BaseModel):
    allowed: bool
    reason: str | None = None
    escalate: bool = False
    fallback: str | None = None
    tripwire_triggered: bool = False


BLOCKED_PHRASES = [
    "ignore previous instructions",
    "wire transfer",
    "crypto payment",
    "send contract",
    "legal agreement",
]

MAX_LENGTH = 1200

guardrail_agent = Agent(
    name="input_guardrail",
    instructions="""
    You are a guardrail agent that checks the input message for any red flags """,
    output_type=AgentOutputSchema(InputGuardrailResult, strict_json_schema=False),
)


@input_guardrail(name="InstagramInputGuardrail")
async def InstagramInputGuardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    message: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input=message, context=context)
    return GuardrailFunctionOutput(
        allowed=result.allowed,
        reason=result.reason,
        escalate=result.escalate,
        fallback=result.fallback,
        output_info=result.output,
        tripwire_triggered=result.output.tripwire_triggered,
    )
