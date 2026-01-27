from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.core.exception import InternalServerErrorException
from app.utils.message_context import build_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


generate_reply_agent = Agent(
    name="generate_reply",
    instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
    model="gpt-4o-mini",
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=GenerateReplyOutput,
)


async def GenerateReply(state: InstagramConversationState):
    input_context = build_message_context(
        state["history"],
        state["user_message"],
    )

    try:
        result = await Runner.run(
            generate_reply_agent,
            input=input_context,
        )
        return result.final_output
    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def generate_ai_reply(state: InstagramConversationState):
    print("Entering Generate AI Reply")

    ai_reply = await GenerateReply(state)

    state["final_reply"] = ai_reply.final_reply or (
        "Thanks for your message! We'll get back to you shortly."
    )

    state["history"].append(
        {
            "role": "assistant",
            "message": state["final_reply"],
        }
    )

    print("Exiting Generate AI Reply")
    return state
