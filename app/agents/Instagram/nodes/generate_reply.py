from agents import Agent, Runner
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import InstagramConversationState
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.message_context import build_message_context, normalize_ai_reply
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


async def GenerateReply(state: InstagramConversationState) -> GenerateReplyOutput:
    print("Enter into Generate Reply")
    try:
        db = get_db()
        collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)

        cursor = (
            collection.find({"thread_id": state.thread_id})
            .sort("timestamp", -1)
            .limit(10)
        )
        docs = await cursor.to_list(length=5)
        docs.reverse()

        if docs and docs[-1]["message"] == state.user_message:
            docs = docs[:-1]

        if not docs:
            docs = [{"sender_type": "AI", "message": "No prior messages."}]
        input_context = build_message_context(docs, state.user_message)
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
    print("Enter into Generate Reply Node")
    try:
        reply = await GenerateReply(state)
        state.reply = normalize_ai_reply(reply)
        return state
    except Exception as e:
        print(f"Error in Generate Reply Node: {str(e)}")
        raise ValueError(f"Generate reply failed: {str(e)}")
