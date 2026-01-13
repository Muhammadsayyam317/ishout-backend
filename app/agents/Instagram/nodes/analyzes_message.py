from agents import Agent, AgentOutputSchema, Runner
from app.Schemas.instagram.message_schema import AnalyzeMessageOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
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
        state.brand_intent = output.get("brand_intent", "")
        state.pricing_mentioned = output.get("pricing_mentioned", False)
        state.negotiation_stage = output.get(
            "negotiation_stage", state.negotiation_stage
        )
        state.negotiation_strategy = output.get(
            "negotiation_strategy", state.negotiation_strategy
        )

        print("✅ Analysis complete")
        return state

    except Exception as e:
        raise InternalServerErrorException(message=f"Analyze message failed: {str(e)}")
