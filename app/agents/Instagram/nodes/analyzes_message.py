from agents import Agent, AgentOutputSchema, Runner
from app.Schemas.instagram.message_schema import AnalyzeMessageOutput
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


analyze_agent = Agent(
    name="analyze_message",
    instructions=ANALYZE_INFLUENCER_DM_PROMPT,
    model="gpt-4o-mini",
    output_type=AgentOutputSchema(AnalyzeMessageOutput, strict_json_schema=False),
)


async def AnalyzeMessage(message: str) -> AnalyzeMessageOutput:
    try:
        print(f"🔍 Analyzing message: {message}")
        print(f"TYPE OF message: {type(message)}")
        result = await Runner.run(
            analyze_agent,
            input=message,
        )
        output: AnalyzeMessageOutput = result.final_output
        print(f"Output from Analyze Message Node: {output}")
        return output
    except Exception as e:
        print(f"Error in Analyze Message Node: {str(e)}")
        raise ValueError(f"Analyze message failed: {str(e)}")


async def node_analyze_message(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("🔍 LangGraph: Analyze node")

    analysis = await AnalyzeMessage(state.user_message)

    state.analysis = analysis
    return state
