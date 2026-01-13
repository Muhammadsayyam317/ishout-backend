from agents import Agent, AgentOutputSchema, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT

analyze_message = Agent(
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

        # Proper input for the agent
        agent_input = InstagramConversationState(
            thread_id=state.thread_id,
            user_message=state.user_message,
            brand_intent=state.brand_intent or "",
            pricing_mentioned=state.pricing_mentioned or False,
            negotiation_stage=state.negotiation_stage,
            negotiation_strategy=state.negotiation_strategy,
        )
        print(f"Agent input: {agent_input}")

        result = await Runner.run(analyze_message, agent_input)
        output: InstagramConversationState = result.final_output
        print(f"Output: {output}")

        # Mutate the state
        state.brand_intent = output.brand_intent
        state.pricing_mentioned = output.pricing_mentioned
        state.negotiation_stage = output.negotiation_stage
        state.negotiation_strategy = output.negotiation_strategy

        print("✅ Analysis complete")
        return state

    except Exception as e:
        raise InternalServerErrorException(message=f"Analyze message failed: {str(e)}")
