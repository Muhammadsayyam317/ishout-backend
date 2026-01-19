import random
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Guardails.output_guardrails import InstagramOutputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
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
    try:
        print(f"Generating reply for thread: {thread_id}")

        db = get_db()
        collection = db.get_collection("instagram_messages")
        cursor = (
            collection.find({"thread_id": thread_id}).sort("timestamp", -1).limit(10)
        )
        docs = await cursor.to_list(length=5)
        docs.reverse()
        if docs and docs[-1]["message"] == message:
            docs = docs[:-1]
        print(f"Docs: {docs}")
        if not docs:
            docs = [{"sender_type": "AI", "message": "No prior messages."}]
        print(f"Docs: {docs}")
        input_context = build_message_context(docs, message)
        print(f"Input context: {input_context}")
        print("🧠 Prompt sent to agent:")
        result = await Runner.run(
            generate_reply_agent,
            input=input_context,
        )
        print(f"Result: {result}")
        output: GenerateReplyOutput = result.final_output
        print(f"Output: {output}")
        return output

    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def node_generate_reply(state: InstagramConversationState):
    if state.next_action == "ASK_AVAILABILITY":
        state.final_reply = "Thanks for your message! 😊 Could you please share your availability for this campaign?"

    elif state.next_action == "ASK_RATE":
        state.final_reply = (
            "Great! Could you please share your rate card for this campaign?"
        )

    elif state.next_action == "ASK_INTEREST":
        state.final_reply = "Would you be interested in collaborating on this campaign?"

    elif state.next_action == "CONFIRM":
        state.final_reply = "Thanks for sharing the details! 🙌 Our team will review everything and get in touch with you soon."

    return state
