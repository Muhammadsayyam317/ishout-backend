from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
)
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
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


async def GenerateReply(message: str, thread_id: str) -> GenerateReplyOutput:
    db = get_db()
    collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)
    cursor = collection.find({"thread_id": thread_id}).sort("timestamp", -1).limit(10)
    docs = await cursor.to_list(length=5)
    docs.reverse()
    if docs and docs[-1]["message"] == message:
        docs = docs[:-1]
    if not docs:
        docs = [{"sender_type": "AI", "message": "No prior messages."}]
    input_context = build_message_context(docs, message)
    try:
        result = await Runner.run(generate_reply_agent, input=input_context)
        return result.final_output
    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def node_generate_reply(state: InstagramConversationState):
    ai_reply = await GenerateReply(state.user_message, state.thread_id)
    state.final_reply = ai_reply.reply
    if not state.final_reply:
        state.final_reply = "Thanks for your message! We'll get back to you shortly."
    return state
