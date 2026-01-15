from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
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
    output_type=AgentOutputSchema(GenerateReplyOutput, strict_json_schema=False),
)


async def GenerateReply(message: str, thread_id: str) -> GenerateReplyOutput:
    try:
        print(f"Generating reply for thread: {thread_id}")

        db = get_db()
        collection = db.get_collection("instagram_messages")
        cursor = (
            collection.find({"thread_id": thread_id}).sort("timestamp", -1).limit(5)
        )
        docs = await cursor.to_list(length=5)
        docs.reverse()
        if docs and docs[-1]["message"] == message:
            docs = docs[:-1]
        if not docs:
            docs = [{"sender_type": "AI", "message": "No prior messages."}]
        input_context = build_message_context(docs, message)
        print("🧠 Prompt sent to agent:")
        print(input_context)
        result = await Runner.run(
            generate_reply_agent,
            input=input_context,
        )

        output: GenerateReplyOutput = result.final_output
        return output

    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def node_generate_reply(
    state: InstagramConversationState,
) -> InstagramConversationState:
    print("✍️ LangGraph: Generate reply node")

    reply = await GenerateReply(
        message=state.user_message,
        thread_id=state.thread_id,
    )

    state.final_reply = reply.final_reply
    print(f"Final reply: {state.final_reply}")

    return state
