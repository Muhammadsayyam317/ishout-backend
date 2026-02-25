from agents.agent_output import AgentOutputSchema
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput, NextAction
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.db.connection import get_db
from bson import ObjectId


async def confirm_details_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering confirm_details_node")
    print("--------------------------------")

    rate = state.get("analysis", {}).get("budget_amount") or state.get(
        "last_offered_price"
    )
    print(f"{Colors.CYAN}Rate: {rate}")
    print("--------------------------------")

    # If we don't have a rate yet, stay in ASK_RATE; otherwise we've noted the rate
    # and now we should acknowledge and move towards closing or sharing details.
    if rate is None:
        state["next_action"] = NextAction.ASK_RATE
    else:
        # We've got a concrete rate from influencer → wait/acknowledge further messages
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE

    prompt = (
        "You are an AI assistant helping a brand negotiate with an influencer on WhatsApp.\n"
        f"The influencer's offered/confirmed rate is: {rate}.\n\n"
        "Write a concise WhatsApp reply that:\n"
        "- Acknowledges their rate positively.\n"
        "- Does NOT ask the influencer to provide or confirm deliverables or timeline "
        "(the brand defines those details).\n"
        "- States that the brand will share the final deliverables and timeline shortly or in the next message.\n"
        "- Does NOT invent specific deliverables or timelines.\n"
        "- Keeps tone professional and friendly.\n"
    )

    history = state.get("history", [])
    agent_input = (
        history
        if history
        else f"Influencer asked about deliverables/timeline. Offered rate: {rate}"
    )

    try:
        result = await Runner.run(
            Agent(
                name="whatsapp_confirm_details",
                instructions=prompt,
                input_guardrails=[WhatsappInputGuardrail],
                output_type=AgentOutputSchema(
                    GenerateReplyOutput, strict_json_schema=False
                ),
            ),
            input=agent_input,
        )
        ai_reply = result.final_output.get(
            "final_reply",
            (
                "Could you please share your rate so we can finalize the details?"
                if rate is None
                else f"Thanks for sharing your rate of ${rate:.2f}. We'll review it and share the deliverables and timeline with you shortly."
            ),
        )
    except Exception as e:
        print(f"[confirm_details_node] AI reply generation failed: {e}")
        ai_reply = (
            "Could you please share your rate so we can finalize the details?"
            if rate is None
            else f"Thanks for sharing your rate of ${rate:.2f}. We'll review it and share the deliverables and timeline with you shortly."
        )

    state["final_reply"] = ai_reply
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_reply})

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        influencer_id = state.get("influencer_id")
        if influencer_id:
            await collection.update_one(
                {"_id": ObjectId(influencer_id)},
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
