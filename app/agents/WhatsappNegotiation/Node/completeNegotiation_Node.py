from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.config.credentials_config import config

# Redis TTL in seconds (5 minutes)
REDIS_TTL = 300

COMPLETE_NEGOTIATION_PROMPT = "Generate a WhatsApp negotiation reply for completing the negotiation with the influencer."


async def complete_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering complete_negotiation_node")
    print("--------------------------------")

    state["conversation_mode"] = "DEFAULT"
    state["human_takeover"] = False
    state["negotiation_completed"] = True
    state["negotiation_status"] = "agreed"

    redis_key = f"whatsapp:negotiation:complete:{state.get('thread_id')}"
    ai_reply = None

    try:
        redis_saver = AsyncRedisSaver.from_conn_string(
            config.REDIS_URL, ttl={"default_ttl": REDIS_TTL}
        )
        checkpointer = await redis_saver.__aenter__()
        ai_reply = await checkpointer.get(redis_key)
    except Exception as e:
        print(f"{Colors.RED}[complete_negotiation_node] Redis read failed: {e}")

    if not ai_reply:
        try:
            result = await Runner.run(
                Agent(
                    name="whatsapp_negotiation_complete",
                    instructions=COMPLETE_NEGOTIATION_PROMPT,
                    input_guardrails=[WhatsappInputGuardrail],
                    output_type=GenerateReplyOutput,
                ),
                input=state.get("history", []),
            )
            ai_reply = result.final_output.get(
                "final_reply", "Thanks for your time! We'll follow up shortly."
            )

            try:
                await checkpointer.set(redis_key, ai_reply)
            except Exception as e:
                print(
                    f"{Colors.RED}[complete_negotiation_node] Redis write failed: {e}"
                )

        except Exception as e:
            print(
                f"{Colors.RED}[complete_negotiation_node] AI reply generation failed: {e}"
            )
            ai_reply = "Thanks for your time! We'll follow up shortly."

    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})
    state["next_action"] = None

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from complete_negotiation_node")
    print("--------------------------------")

    return state
