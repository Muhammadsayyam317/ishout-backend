from agents import Agent, Runner
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.message_context import build_message_context
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


async def GenerateReply(state: InstagramConversationState) -> GenerateReplyOutput:
    """
    Generates the AI reply using the last few messages and negotiation bounds.
    """
    try:
        db = get_db()
        collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)

        # Fetch last 5-10 messages
        cursor = (
            collection.find({"thread_id": state.thread_id})
            .sort("timestamp", -1)
            .limit(10)
        )
        docs = await cursor.to_list(length=5)
        docs.reverse()

        # Remove duplicate latest user message
        if docs and docs[-1]["message"] == state.user_message:
            docs = docs[:-1]

        if not docs:
            docs = [{"sender_type": "AI", "message": "No prior messages."}]

        # Build conversation history
        input_context = build_message_context(docs, state.user_message)

        # Fill min/max in prompt dynamically
        instructions = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
            min_price=state.min_price, max_price=state.max_price
        )

        result = await Runner.run(
            Agent(
                name="generate_reply",
                instructions=instructions,
                output_type=GenerateReplyOutput,
            ),
            input={
                "conversation": input_context,
                "next_action": getattr(state, "next_action", None),
                "strategy": state.strategy.value if state.strategy else None,
                "min_price": state.min_price,
                "max_price": state.max_price,
            },
        )

        output: GenerateReplyOutput = result.final_output
        return output

    except Exception as e:
        raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def node_generate_reply(
    state: InstagramConversationState,
) -> InstagramConversationState:
    """
    Node to generate AI reply and attach to state.
    """
    print("✍️ LangGraph: Generate reply node")
    try:
        reply = await GenerateReply(state)
        state.reply = reply
        print(f"Reply: {state.reply}")
    except Exception as e:
        print("⚠️ Guardrail or generation failure:", str(e))
    return state
