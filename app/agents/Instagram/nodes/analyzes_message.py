from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Schemas.instagram.message_schema import AnalyzeMessageOutput
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


async def AnalyzeMessage(message: str) -> AnalyzeMessageOutput:
    print("Entering into Analyze messgae")
    try:
        result = await Runner.run(
            Agent(
                name="analyze_message",
                instructions=ANALYZE_INFLUENCER_DM_PROMPT,
                input_guardrails=[InstagramInputGuardrail],
                output_type=AnalyzeMessageOutput,
            ),
            input=message,
        )
        print("user meaage", message)
        output: AnalyzeMessageOutput = result.final_output
        print("Exiting from Analyze Message")
        return output
    except Exception as e:
        print(f"Error in Analyze Message Node: {str(e)}")
        raise ValueError(f"Analyze message failed: {str(e)}")


async def node_analyze_message(
    state: InstagramConversationState,
) -> InstagramConversationState:
    analysis = await AnalyzeMessage(state.user_message)
    state.analysis = analysis
    return state
