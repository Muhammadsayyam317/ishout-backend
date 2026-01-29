from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    AnalyzeMessageOutput,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT
import logging

logger = logging.getLogger(__name__)


async def analyze_intent(state: InstagramConversationState):
    result = await Runner.run(
        Agent(
            name="analyze_message",
            instructions=ANALYZE_INFLUENCER_DM_PROMPT,
            input_guardrails=[InstagramInputGuardrail],
            output_type=AnalyzeMessageOutput,
        ),
        input=state["user_message"],
    )

    analysis: AnalyzeMessageOutput = result.final_output

    state["analysis"] = analysis
    state["intent"] = analysis.get("intent", "unclear")

    state.setdefault("influencerResponse", {})

    if analysis.get("pricing_mentioned") and analysis.get("budget_amount") is not None:
        state["influencerResponse"]["rate"] = analysis["budget_amount"]

    if analysis.get("availability_mentioned"):
        state["influencerResponse"]["availability"] = "provided"

    if analysis.get("interest_mentioned"):
        state["influencerResponse"]["interest"] = True

    # -------- Next Action --------
    state["next_action"] = analysis.get(
        "recommended_next_action",
        "wait_or_acknowledge",
    )

    logger.debug(
        "AnalyzeIntent | intent=%s | next_action=%s",
        state["intent"],
        state["next_action"],
    )

    return state
