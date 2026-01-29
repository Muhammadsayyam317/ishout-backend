from agents import Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    GenerateReplyOutput,
)
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT
from app.utils.message_context import build_message_context


async def generate_ai_reply(state: InstagramConversationState):
    print("Entering into Node Generate AI Reply")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    min_price = state["pricingRules"].get("minPrice", 0)
    max_price = state["pricingRules"].get("maxPrice", 0)

    prompt = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
        min_price=min_price, max_price=max_price
    )

    ai_reply: GenerateReplyOutput = await Runner.run(
        prompt,
        model="gpt-4o-mini",
        input_guardrails=[InstagramInputGuardrail],
        output_guardrails=[InstagramOutputGuardrail],
        output_type=GenerateReplyOutput,
        input=build_message_context(state["history"], state["user_message"]),
    )

    reply_text = ai_reply.get("final_reply") or "Got it — will update you shortly."
    state["final_reply"] = reply_text
    state["history"].append({"role": "assistant", "message": reply_text})

    print("Exiting from Node Generate AI Reply")
    print("--------------------------------")
    print(state)
    print("--------------------------------")
    return state
