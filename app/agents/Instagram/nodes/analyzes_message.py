from agents import Agent, AgentOutputSchema, Runner
from app.Schemas.instagram.message_schema import AnalyzeMessageOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


analyze_agent = Agent(
    name="analyze_message",
    instructions=ANALYZE_INFLUENCER_DM_PROMPT,
    output_type=AgentOutputSchema(AnalyzeMessageOutput, strict_json_schema=False),
)


async def node_analyze_message(
    state: InstagramConversationState,
) -> InstagramConversationState:
    try:
        print(f"🔍 Analyzing message: {state.user_message}")
        result = await Runner.run(
            analyze_agent,
            input=state.user_message,
        )

        output: dict = result.final_output or {}
        state.brand_intent = output.brand_intent or ""
        state.pricing_mentioned = output.pricing_mentioned or False
        state.negotiation_stage = output.negotiation_stage or state.negotiation_stage
        state.negotiation_strategy = (
            output.negotiation_strategy or state.negotiation_strategy
        )
        print("✅ Analysis complete")
        return state
    except Exception as e:
        raise ValueError(
            f"Analyze message failed for thread_id: {state.thread_id} - {str(e)}"
        )
