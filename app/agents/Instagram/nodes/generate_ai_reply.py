from agents import Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.utils.message_context import build_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


async def GenerateReply(state: dict) -> dict:
    result = await Runner.run(
        NEGOTIATE_INFLUENCER_DM_PROMPT.format(
            min_price=state["pricingRules"]["minPrice"],
            max_price=state["pricingRules"]["maxPrice"],
        ),
        model="gpt-4o-mini",
        input_guardrails=[InstagramInputGuardrail],
        output_guardrails=[InstagramOutputGuardrail],
        output_type=GenerateReplyOutput,
        input=build_message_context(state["history"], state["user_message"]),
    )
    return result.final_output


async def generate_ai_reply(state: dict):
    print("Entering into Generate AI Reply")
    ai_reply = await GenerateReply(state)
    reply_text = ai_reply.get("final_reply") or "Got it — will update you shortly."
    state["final_reply"] = reply_text
    state["history"].append({"sender_type": "AI", "message": reply_text})
    print("Exiting from Generate AI Reply")
    return state
