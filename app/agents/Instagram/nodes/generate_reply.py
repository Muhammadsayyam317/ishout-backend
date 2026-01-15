from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
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

        history = []
        for doc in docs:
            role = "assistant" if doc["sender_type"] == "AI" else "user"
            history.append(
                {
                    "role": role,
                    "content": doc["message"],
                }
            )

        print("🧠 Conversation history sent to agent:")
        for h in history:
            print(f"{h['role']}: {h['content']}")

        result = await Runner.run(
            generate_reply_agent,
            input=message,
            history=history,
        )

        output: GenerateReplyOutput = result.final_output
        print(f"Output from Generate Reply Node: {output}")
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
