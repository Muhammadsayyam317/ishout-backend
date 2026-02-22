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


from app.db.connection import get_db
from bson import ObjectId


async def close_conversation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering close_conversation_node")
    print("--------------------------------")

    state["negotiation_status"] = "closed"
    try:
        result = await Runner.run(
            Agent(
                name="whatsapp_close_conversation",
                instructions="Generate a WhatsApp negotiation reply for closing the conversation with the influencer.",
                input_guardrails=[WhatsappInputGuardrail],
                output_type=dict,
            ),
            input=state.get("history", []),
        )
        ai_reply = result.final_output.get(
            "final_reply", "Thank you! Looking forward to working together."
        )
    except Exception as e:
        print(f"[close_conversation_node] AI generation failed: {e}")
        ai_reply = "Thank you! Looking forward to working together."

    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})
    state["next_action"] = None

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "negotiation_status": state["negotiation_status"],
                    "final_reply": state["final_reply"],
                    "history": state["history"],
                }
            },
        )
    except Exception as e:
        print(f"[close_conversation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from close_conversation_node")
    print("--------------------------------")
    return state
