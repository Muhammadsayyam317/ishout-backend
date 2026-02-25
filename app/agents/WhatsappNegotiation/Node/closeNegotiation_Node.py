from agents.agent_output import AgentOutputSchema
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.db.connection import get_db
from bson import ObjectId
from app.utils.prompts import WHATSAPP_CLOSE_CONVERSATION_INSTRUCTIONS
from app.utils.message_context import (
    get_history_list,
    set_history_list,
    history_to_agent_messages,
)


async def close_conversation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering close_conversation_node")
    print("--------------------------------")

    history = get_history_list(state)
    set_history_list(state, history)

    state["negotiation_status"] = "closed"
    try:
        result = await Runner.run(
            Agent(
                name="whatsapp_close_conversation",
                instructions=WHATSAPP_CLOSE_CONVERSATION_INSTRUCTIONS,
                input_guardrails=[WhatsappInputGuardrail],
                output_type=AgentOutputSchema(
                    GenerateReplyOutput, strict_json_schema=False
                ),
            ),
            input=history_to_agent_messages(history),
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
