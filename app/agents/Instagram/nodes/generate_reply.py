import random
from agents import Agent, Runner
from app.Guardails.input_guardrails import InstagramInputGuardrail
from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.Schemas.instagram.negotiation_schema import (
    InstagramConversationState,
    SenderType,
)
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.message_context import build_message_context, normalize_ai_reply
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


# async def GenerateReply(state: InstagramConversationState) -> GenerateReplyOutput:
#     print("Enter into Generate Reply")
#     try:
#         db = get_db()
#         collection = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)

#         cursor = (
#             collection.find({"thread_id": state.thread_id})
#             .sort("timestamp", -1)
#             .limit(10)
#         )
#         docs = await cursor.to_list(length=5)
#         docs.reverse()

#         if docs and docs[-1]["message"] == state.user_message:
#             docs = docs[:-1]

#         if not docs:
#             docs = [{"sender_type": "AI", "message": "No prior messages."}]
#         input_context = build_message_context(docs, state.user_message)
#         instructions = NEGOTIATE_INFLUENCER_DM_PROMPT.format(
#             min_price=state.min_price, max_price=state.max_price
#         )

#         result = await Runner.run(
#             Agent(name="generate_reply", instructions=instructions),
#             input={
#                 "conversation": input_context,
#                 "next_action": getattr(state, "next_action", None),
#                 "strategy": state.strategy.value if state.strategy else None,
#                 "min_price": state.min_price,
#                 "max_price": state.max_price,
#             },
#         )
#         output: GenerateReplyOutput = result.final_output
#         return output

#     except Exception as e:
#         raise InternalServerErrorException(f"Error generating reply: {str(e)}")


async def GenerateReply(state: InstagramConversationState) -> GenerateReplyOutput:
    try:
        print(f"Generating reply for thread: {state.thread_id}")

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
            docs = [
                {"sender_type": SenderType.AI.value, "message": "No prior messages."}
            ]
        print(f"Docs: {docs}")
        input_context = build_message_context(docs, state.user_message)
        print("🧠 Prompt sent to agent:")

        result = await Runner.run(
            Agent(
                name="generate_reply",
                instructions=NEGOTIATE_INFLUENCER_DM_PROMPT,
                model="gpt-4o-mini",
            ),
            input={
                "conversation": input_context,
                "next_action": getattr(state, "next_action", None),
                "strategy": state.strategy.value if state.strategy else None,
                "min_price": state.min_price,
                "max_price": state.max_price,
            },
        )
        print(f"Result: {result}")
        output: GenerateReplyOutput = result.final_output
        print(f"Output: {output}")
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
        print("⚠️ Guardrail or generation failure:", str(e))
        print(f"Final reply: {state.reply}")
        fallbacks = [
            "Got it 👍 Let me check the best options for you.",
            "Thanks for sharing! I’ll review and update you shortly.",
            "Perfect, give me a moment to look into this.",
            "Thanks for your message! Let me check and get back to you shortly.",
            "Thank you for your message. I'll get back to you shortly.",
            "Happy to explore this — just need a few details before moving forward.",
            "Let me check on this. Can you clarify the scope and timeline?",
            "Got it. Could you share a bit more detail so I can respond properly?",
        ]
        state.reply = random.choice(fallbacks)
        print(f"Fallback reply: {state.reply}")
    return state
