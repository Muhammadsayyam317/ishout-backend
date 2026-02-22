from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.db.connection import get_db
from bson import ObjectId


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

    next_action = (
        NextAction.ASK_RATE if rate is None else NextAction.CONFIRM_DELIVERABLES
    )
    state["next_action"] = next_action

    try:
        result = await Runner.run(
            Agent(
                name="whatsapp_confirm_details",
                instructions="Generate a WhatsApp negotiation reply for confirming the details with the influencer.",
                input_guardrails=[WhatsappInputGuardrail],
                output_type=dict,
            ),
            input=state.get("history", []),
        )
        ai_reply = result.final_output.get(
            "final_reply",
            (
                "Could you please provide the required details?"
                if rate is None
                else f"Thanks for sharing your rate of ${rate:.2f}. Could you confirm the deliverables and timeline?"
            ),
        )
    except Exception as e:
        print(f"[confirm_details_node] AI reply generation failed: {e}")
        ai_reply = (
            "Could you please provide the required details?"
            if rate is None
            else f"Thanks for sharing your rate of ${rate:.2f}. Could you confirm the deliverables and timeline?"
        )

    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "final_reply": state["final_reply"],
                    "history": state["history"],
                    "next_action": state["next_action"],
                }
            },
        )
    except Exception as e:
        print(f"[confirm_details_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}AI Generated Reply: {ai_reply}")
    print(f"{Colors.YELLOW}Exiting from confirm_details_node")
    print("--------------------------------")

    return state
