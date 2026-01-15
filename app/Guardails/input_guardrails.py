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

    result = await Runner.run(
        guardrail_agent,
        input=message,
        context=context,
    )

    guardrail_output: InputGuardrailResult = result.final_output

    return GuardrailFunctionOutput(
        allowed=guardrail_output.allowed,
        reason=guardrail_output.reason,
        escalate=guardrail_output.escalate,
        fallback=guardrail_output.fallback,
        output_info=None,  # input guardrails usually don't need this
        tripwire_triggered=guardrail_output.tripwire_triggered,
    )


# analyze_message = Agent(
#     name="analyze_message",
#     instructions=ANALYZE_INFLUENCER_DM_PROMPT,
#     input_guardrails=[InstagramInputGuardrail],
#     output_guardrails=[InstagramOutputGuardrail],
#     output_type=AgentOutputSchema(InstagramConversationState, strict_json_schema=False),
# )
