from agents.agent_output import AgentOutputSchema
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.db.connection import get_db
from bson import ObjectId


async def complete_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering complete_negotiation_node")
    print("--------------------------------")

    state["conversation_mode"] = "DEFAULT"
    state["human_takeover"] = False
    state["negotiation_completed"] = True
    state["negotiation_status"] = "agreed"

    try:
        result = await Runner.run(
            Agent(
                name="whatsapp_negotiation_complete",
                instructions="Generate a WhatsApp negotiation reply for completing the negotiation with the influencer.",
                input_guardrails=[WhatsappInputGuardrail],
                output_type=AgentOutputSchema(
                    GenerateReplyOutput, strict_json_schema=False
                ),
            ),
            input=state.get("history", []),
        )
        ai_reply = result.final_output.get(
            "final_reply", "Thanks for your time! We'll follow up shortly."
        )
    except Exception as e:
        print(f"[complete_negotiation_node] AI generation failed: {e}")
        ai_reply = "Thanks for your time! We'll follow up shortly."

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
                    "negotiation_completed": state["negotiation_completed"],
                    "human_takeover": state["human_takeover"],
                    "conversation_mode": state["conversation_mode"],
                    "final_reply": state["final_reply"],
                    "history": state["history"],
                    "next_action": state["next_action"],
                }
            },
        )
    except Exception as e:
        print(f"[complete_negotiation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from complete_negotiation_node")
    print("--------------------------------")

    return state
