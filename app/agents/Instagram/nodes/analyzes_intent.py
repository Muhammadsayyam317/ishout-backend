from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    AnalyzeMessageOutput,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


async def AnalyzeMessage(message: str) -> AnalyzeMessageOutput:
    result = await Runner.run(
        Agent(
            name="analyze_message",
            instructions=ANALYZE_INFLUENCER_DM_PROMPT,
            input_guardrails=[InstagramInputGuardrail],
            output_type=AnalyzeMessageOutput,
        ),
        input=message,
    )
    return result.final_output


async def analyze_intent(state: InstagramConversationState):
    analysis = await AnalyzeMessage(state["user_message"])
    state["analysis"] = analysis
    state["intent"] = analysis.intent

    # Map extracted facts
    if analysis.pricing_mentioned and analysis.budget_amount:
        state["influencerResponse"]["rate"] = analysis.budget_amount
        state["currency"] = analysis.currency

    if analysis.availability_mentioned:
        state["influencerResponse"]["availability"] = "provided"

    if analysis.interest_mentioned:
        state["influencerResponse"]["interest"] = True

    # 🔑 SINGLE ROUTING AUTHORITY
    state["next_action"] = analysis.recommended_next_action
    print(f"Next action: {state['next_action']}")
    print("Exiting from Node Analyze Intent")
    return state
