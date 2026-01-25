from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    AnalyzeMessageOutput,
    NextAction,
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


async def node_analyze_message(state: InstagramConversationState):
    print("Entering into Node Analyze Message")
    analysis = await AnalyzeMessage(state.user_message)
    state.analysis = analysis

    if analysis.is_question:
        state.next_action = NextAction.ANSWER_QUESTION
        return state

    if "availability" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_AVAILABILITY
    elif "rate_card" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_RATE
    elif "interest" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_INTEREST
    else:
        state.next_action = NextAction.CONFIRM
    print("Exiting Node Analyze Message")
    return state
