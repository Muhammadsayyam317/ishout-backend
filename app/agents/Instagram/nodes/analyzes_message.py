from agents import Agent
from agents import AgentOutputSchema
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException


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

        result = await analyze_message_agent.ainvoke(
            {
                "message": state.user_message,
                "thread_id": state.thread_id,
            }
        )

        # ✅ Mutate state (LangGraph requirement)
        state.brand_intent = result.brand_intent
        state.pricing_mentioned = result.pricing_mentioned
        state.negotiation_stage = result.negotiation_stage
        state.negotiation_strategy = result.negotiation_strategy

        print("✅ Analysis complete")
        print(f"Intent: {state.brand_intent}")
        print(f"Pricing: {state.pricing_mentioned}")
        print(f"Stage: {state.negotiation_stage}")
        print(f"Strategy: {state.negotiation_strategy}")

        return state

    except Exception as e:
        raise InternalServerErrorException(message=f"Analyze message failed: {str(e)}")
