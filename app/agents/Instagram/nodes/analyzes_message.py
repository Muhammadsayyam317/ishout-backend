from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Schemas.instagram.negotiation_schema import (
    AnalyzeMessageOutput,
    InstagramConversationState,
    NextAction,
)
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


async def AnalyzeMessage(message: str) -> AnalyzeMessageOutput:
    try:
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
    except Exception as e:
        raise ValueError(f"Analyze message failed: {str(e)}")


async def node_analyze_message(state: InstagramConversationState):
    analysis = await AnalyzeMessage(state.user_message)
    state.analysis = analysis

    if analysis.is_question:
        state.next_action = NextAction.ANSWER_QUESTION
    elif "availability" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_AVAILABILITY
    elif "rate_card" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_RATE
    elif "interest" in analysis.missing_required_details:
        state.next_action = NextAction.ASK_INTEREST
    else:
        state.next_action = NextAction.CONFIRM

    return state
