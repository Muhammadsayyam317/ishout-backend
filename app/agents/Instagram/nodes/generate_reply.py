from agents import Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    NextAction,
)
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.message_context import build_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT
from agents import Agent

# GPT Agent setup
generate_reply_agent = Agent(
    name="generate_reply",
    instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
    model="gpt-4o-mini",
    input_guardrails=[InstagramInputGuardrail],
    output_guardrails=[InstagramOutputGuardrail],
    output_type=GenerateReplyOutput,
)


# Function to call AI
async def GenerateReply(message: str, thread_id: str) -> GenerateReplyOutput:
    try:
        db = get_db()
        collection = db.get_collection("instagram_messages")

        cursor = (
            collection.find({"thread_id": thread_id}).sort("timestamp", -1).limit(10)
        )
        docs = await cursor.to_list(length=5)
        docs.reverse()
        if docs and docs[-1]["message"] == message:
            docs = docs[:-1]
        if not docs:
            docs = [{"sender_type": "AI", "message": "No prior messages."}]

        input_context = build_message_context(docs, message)

        result = await Runner.run(generate_reply_agent, input=input_context)
        output: GenerateReplyOutput = result.final_output
        return output

    except Exception as e:
        raise InternalServerErrorException(f"Error generating AI reply: {str(e)}")


async def node_generate_reply(state: InstagramConversationState):
    if state.next_action == NextAction.ASK_AVAILABILITY:
        state.final_reply = (
            "Could you please share your availability for this campaign?"
        )
    elif state.next_action == NextAction.ASK_RATE:
        state.final_reply = "Please share your rate card for this campaign."
    elif state.next_action == NextAction.ASK_INTEREST:
        state.final_reply = "Are you interested in collaborating on this campaign?"
    elif state.next_action == NextAction.CONFIRM:
        state.final_reply = "Thanks for sharing your details! Our team will review and get in touch soon."
    elif state.next_action == NextAction.ANSWER_QUESTION:
        ai_output = await GenerateReply(state.user_message, state.thread_id)
        state.final_reply = ai_output.final_reply

    return state
