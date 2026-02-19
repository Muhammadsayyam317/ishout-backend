from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.config.credentials_config import config

# Redis TTL in seconds (5 minutes)
REDIS_TTL = 300


CLOSE_CONVERSATION_PROMPT = "Generate a WhatsApp negotiation reply for closing the conversation with the influencer."


async def close_conversation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering close_conversation_node")
    print("--------------------------------")

    state["negotiation_status"] = "closed"
    redis_key = f"whatsapp:negotiation:close:{state.get('thread_id')}"
    ai_reply = None

    # Try reading from Redis
    try:
        redis_saver = AsyncRedisSaver.from_conn_string(
            config.REDIS_URL, ttl={"default_ttl": REDIS_TTL}
        )
        checkpointer = await redis_saver.__aenter__()
        ai_reply = await checkpointer.get(redis_key)
    except Exception as e:
        print(f"{Colors.RED}[close_conversation_node] Redis read failed: {e}")

    # Generate AI reply if not cached
    if not ai_reply:
        try:
            result = await Runner.run(
                Agent(
                    name="whatsapp_close_conversation",
                    instructions=CLOSE_CONVERSATION_PROMPT,
                    input_guardrails=[WhatsappInputGuardrail],
                    output_type=GenerateReplyOutput,
                ),
                input=state.get("history", []),
            )
            ai_reply = result.final_output.get(
                "final_reply", "Thank you! Looking forward to working together."
            )

            # Save to Redis for 5 minutes
            try:
                await checkpointer.set(redis_key, ai_reply)
            except Exception as e:
                print(f"{Colors.RED}[close_conversation_node] Redis write failed: {e}")

        except Exception as e:
            print(
                f"{Colors.RED}[close_conversation_node] AI reply generation failed: {e}"
            )
            ai_reply = "Thank you! Looking forward to working together."

    # Save final reply in state and history
    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})
    state["next_action"] = None

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from close_conversation_node")
    print("--------------------------------")

    return state
