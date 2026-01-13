from agents import Agent
from agents import AgentOutputSchema
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT
from app.Schemas.instagram.negotiation_schema import InstagramConversationState


analyze_message_agent = Agent(
    name="analyze_message",
    instructions=ANALYZE_INFLUENCER_DM_PROMPT,
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=AgentOutputSchema(InstagramConversationState, strict_json_schema=False),
)


async def node_analyze_message(state: InstagramConversationState):
    print(f"Analyzing message: {state.user_message}")
    result = await analyze_message_agent.ainvoke(state)
    state.brand_intent = result.brand_intent
    state.pricing_mentioned = result.pricing_mentioned
    state.negotiation_stage = result.negotiation_stage
    state.negotiation_strategy = result.negotiation_strategy
    print(f"Brand intent: {state.brand_intent}")
    print(f"Pricing mentioned: {state.pricing_mentioned}")
    print(f"Negotiation stage: {state.negotiation_stage}")
    print(f"Negotiation strategy: {state.negotiation_strategy}")

    return state
