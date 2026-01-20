from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

from app.Schemas.instagram.message_schema import (
    OutputGuardrailResult,
)
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput


@output_guardrail(name="InstagramOutputGuardrail")
async def InstagramOutputGuardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: GenerateReplyOutput,
) -> GuardrailFunctionOutput:

    result = await Runner.run(
        Agent(
            name="output_guardrail_evaluator",
            instructions="""Review the iShout Instagram DM.iShout is a platform for managing social media campaigns and providing influncers to the brand for their campaigns in multiple platforms.Providing a reply to an Instagram DM.Regarding the reply, you must review it before it is sent.
            """,
            output_type=OutputGuardrailResult,
        ),
        output.reply,
        context=ctx.context,
    )
    print("🛡️ Output Guardrail result:", result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.reason,
        tripwire_triggered=False,
    )
