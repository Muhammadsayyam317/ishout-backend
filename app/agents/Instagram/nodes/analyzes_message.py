from agents import Agent, AgentOutputSchema, Runner
from app.Schemas.instagram.message_schema import AnalyzeMessageOutput
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NegotiationStage,
    NegotiationStrategy,
)
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

        output: AnalyzeMessageOutput = result.final_output
        state.brand_intent = output.brand_intent or ""
        state.pricing_mentioned = bool(output.pricing_mentioned)

        if isinstance(output.negotiation_stage, NegotiationStage):
            state.negotiation_stage = output.negotiation_stage

        if isinstance(output.negotiation_strategy, NegotiationStrategy):
            state.negotiation_strategy = output.negotiation_strategy

        print("✅ Analysis complete")
        return state
    except Exception as e:
        raise ValueError(
            f"Analyze message failed for thread_id: {state.thread_id} - {str(e)}"
        )
