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
    """Run AI to extract intent and budget, availability, interest."""
    result: AnalyzeMessageOutput = await Runner.run(
        Agent(
            name="analyze_message",
            instructions=ANALYZE_INFLUENCER_DM_PROMPT,
            input_guardrails=[InstagramInputGuardrail],
            output_type=AnalyzeMessageOutput,
        ),
        input=state["user_message"],
    )

    state["analysis"] = result
    state["intent"] = result.get("intent", "unclear")

    if result.get("pricing_mentioned") and result.get("budget_amount"):
        state["influencerResponse"]["rate"] = result["budget_amount"]
        state["influencerResponse"]["currency"] = result.get("currency", "USD")

    if result.get("availability_mentioned"):
        state["influencerResponse"]["availability"] = "provided"

    if result.get("interest_mentioned"):
        state["influencerResponse"]["interest"] = True

    state["next_action"] = result.get("recommended_next_action", "wait_or_acknowledge")
    logger.debug(f"Next action determined: {state['next_action']}")
    return state
