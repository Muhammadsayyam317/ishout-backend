from agents import Runner, Agent
from agents.exceptions import InputGuardrailTripwireTriggered

from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    GenerateReplyOutput,
)
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT
from app.utils.message_context import build_message_context


async def generate_ai_reply(state: InstagramConversationState):
    min_price = state.get("pricing_rules", {}).get("minPrice")
    max_price = state.get("pricing_rules", {}).get("maxPrice")

    if min_price is None or max_price is None:
        reply_text = (
            "Thanks for sharing your rate. Our team will review it and follow up."
        )
        state["negotiation_mode"] = "manual"
        state["manual_reason"] = "Pricing rules missing"
        state["final_reply"] = reply_text
        state["history"].append({"role": "assistant", "message": reply_text})
        return state

    prompt = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
        min_price=min_price,
        max_price=max_price,
    )

    try:
        result = await Runner.run(
            Agent(
                name="generate_reply",
                instructions=prompt,
                input_guardrails=[InstagramInputGuardrail],
                output_guardrails=[InstagramOutputGuardrail],
                output_type=GenerateReplyOutput,
            ),
            input=build_message_context(
                state["history"],
                state["user_message"],
            ),
        )

        reply_text = result.final_output["final_reply"]
        state["negotiation_mode"] = "automatic"

    except InputGuardrailTripwireTriggered as e:
        reply_text = (
            e.fallback or "Thanks for sharing your rate. Our team will follow up."
        )
        state["negotiation_mode"] = "manual"
        state["manual_reason"] = e.reason

    state["final_reply"] = reply_text
    state["history"].append({"role": "assistant", "message": reply_text})
    return state
