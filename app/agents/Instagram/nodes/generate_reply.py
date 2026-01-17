from agents import Agent, Runner
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.message_context import build_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


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
        result = await Runner.run(
            Agent(
                name="generate_reply",
                instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
                output_type=GenerateReplyOutput,
            ),
            input=input_context,
        )
        output: GenerateReplyOutput = result.final_output
        print(f"Output: {output}")
        return output

    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def node_generate_reply(
    state: dict,
) -> InstagramConversationState:
    print("✍️ LangGraph: Generate reply node")
    try:
        reply = await GenerateReply(
            message=state.user_message,
            thread_id=state.thread_id,
        )
        state.reply = reply
        print(f"Reply: {state.reply}")
    except Exception as e:
        print("⚠️ Guardrail or generation failure:", str(e))
        print(f"Reply: {state.reply}")
        # FALLBACK
        # fallbacks = [
        #     "Got it 👍 Let me check the best options for you.",
        #     "Thanks for sharing! I’ll review and update you shortly.",
        #     "Perfect, give me a moment to look into this.",
        # ]
        # state.reply = random.choice(fallbacks)
        print(f"Fallback reply: {state.reply}")
    return state
