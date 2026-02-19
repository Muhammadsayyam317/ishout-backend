from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.config.credentials_config import config

# Redis TTL in seconds (5 minutes)
REDIS_TTL = 300
CONFIRM_DETAILS_PROMPT = "Generate a WhatsApp negotiation reply for confirming the details with the influencer."


async def confirm_details_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering confirm_details_node")
    print("--------------------------------")

    rate = state.get("analysis", {}).get("budget_amount") or state.get(
        "last_offered_price"
    )
    print(f"{Colors.CYAN}Rate: {rate}")
    print("--------------------------------")

    redis_key = f"whatsapp:negotiation:confirm:{state.get('thread_id')}"
    ai_reply = None

    # Try reading from Redis
    try:
        redis_saver = AsyncRedisSaver.from_conn_string(
            config.REDIS_URL, ttl={"default_ttl": REDIS_TTL}
        )
        checkpointer = await redis_saver.__aenter__()
        ai_reply = await checkpointer.get(redis_key)
    except Exception as e:
        print(f"{Colors.RED}[confirm_details_node] Redis read failed: {e}")

    # Generate AI reply if not cached
    if not ai_reply:
        try:
            if rate is None:
                next_action = NextAction.ASK_RATE
            else:
                next_action = NextAction.CONFIRM_DELIVERABLES

            result = await Runner.run(
                Agent(
                    name="whatsapp_confirm_details",
                    instructions=CONFIRM_DETAILS_PROMPT,
                    input_guardrails=[WhatsappInputGuardrail],
                    output_type=GenerateReplyOutput,
                ),
                input=state.get("history", []),
            )
            ai_reply = result.final_output.get(
                "final_reply", "Could you please provide the required details?"
            )

            # Save to Redis for 5 minutes
            try:
                await checkpointer.set(redis_key, ai_reply)
            except Exception as e:
                print(f"{Colors.RED}[confirm_details_node] Redis write failed: {e}")

            state["next_action"] = next_action

        except Exception as e:
            print(f"{Colors.RED}[confirm_details_node] AI reply generation failed: {e}")
            ai_reply = (
                "Could you please confirm your rate for this collaboration?"
                if rate is None
                else f"Thanks for sharing your rate of ${rate:.2f}. Could you confirm the deliverables and timeline?"
            )
            state["next_action"] = (
                NextAction.ASK_RATE if rate is None else NextAction.CONFIRM_DELIVERABLES
            )

    # Save final reply in state and history
    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from confirm_details_node")
    print("--------------------------------")

    return state
