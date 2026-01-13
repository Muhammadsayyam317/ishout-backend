from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.core.exception import InternalServerErrorException
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


analyze_message_agent = Agent(
    name="analyze_message",
    instructions=ANALYZE_INFLUENCER_DM_PROMPT,
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=AgentOutputSchema(InstagramConversationState, strict_json_schema=False),
)


async def node_analyze_message(
    state: InstagramConversationState,
) -> InstagramConversationState:
    try:
        print(f"🔍 Analyzing message: {state.user_message}")

        result = await Runner.run(
            analyze_message_agent,
            {
                "message": state.user_message,
                "thread_id": state.thread_id,
            },
        )
        print(f"Raw agent result: {result}")

        # ✅ result.final_output is your Pydantic model
        output: InstagramConversationState = result.final_output

        state.brand_intent = output.brand_intent
        state.pricing_mentioned = output.pricing_mentioned
        state.negotiation_stage = output.negotiation_stage
        state.negotiation_strategy = output.negotiation_strategy

        print("✅ Analysis complete")
        return state

    except Exception as e:
        raise InternalServerErrorException(message=f"Analyze message failed: {str(e)}")
