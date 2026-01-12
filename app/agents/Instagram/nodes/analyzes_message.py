from enum import Enum
from typing import Optional
from agents import Agent, RunContextWrapper, Runner
from pydantic import BaseModel
from agents import AgentOutputSchema
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.core.exception import InternalServerErrorException
from app.utils.prompts import ANALYZE_INFLUENCER_DM_PROMPT


class NegotiationStage(Enum):
    INITIAL = "INITIAL"
    COUNTER = "COUNTER"
    FINAL = "FINAL"


class NegotiationStrategy(Enum):
    SOFT = "SOFT"
    VALUE_BASED = "VALUE_BASED"
    WALK_AWAY = "WALK_AWAY"


class AnalyzeMessageResult(BaseModel):
    brand_intent: str
    pricing_mentioned: bool
    campaign_details_missing: bool
    next_action: str
    negotiation_stage: NegotiationStage = NegotiationStage.INITIAL
    negotiation_strategy: NegotiationStrategy = NegotiationStrategy.SOFT
    ai_draft: str = ""
    human_approved: Optional[bool] = None


agent = Agent(
    name="analyze_message",
    instructions=ANALYZE_INFLUENCER_DM_PROMPT,
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=AgentOutputSchema(AnalyzeMessageResult, strict_json_schema=False),
)


async def node_analyze_message(state: dict):
    try:
        influencerMessage = state.get("user_message")
        if not influencerMessage:
            raise ValueError("influencerMessage is required")
        result = await Runner.run(
            agent, input=influencerMessage, context=RunContextWrapper(state)
        )
        state["brand_intent"] = result.brand_intent
        state["pricing_mentioned"] = result.pricing_mentioned
        state["campaign_details_missing"] = result.campaign_details_missing
        state["next_action"] = result.next_action
        state["negotiation_stage"] = result.negotiation_stage
        state["negotiation_strategy"] = result.negotiation_strategy
        state["ai_draft"] = result.ai_draft
        state["human_approved"] = result.human_approved
    except Exception as e:
        raise InternalServerErrorException(message=str(e))
    return state
