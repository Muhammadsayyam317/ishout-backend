from datetime import datetime, timezone
from agents.agent_output import AgentOutputSchema
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput, NextAction
from app.utils.printcolors import Colors
from agents import Agent, Runner
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.db.connection import get_db
from bson import ObjectId
from app.utils.prompts import WHATSAPP_CONFIRM_DETAILS_SUFFIX
from app.utils.message_context import (
    get_history_list,
    set_history_list,
    history_to_agent_messages,
)
from app.config.credentials_config import config


async def confirm_details_node(state: WhatsappNegotiationState):
    history = get_history_list(state)
    set_history_list(state, history)

    rate = state.get("analysis", {}).get("budget_amount") or state.get(
        "last_offered_price"
    )

    # If we don't have a rate yet, stay in ASK_RATE; otherwise we've noted the rate
    # and now we should acknowledge and move towards closing or sharing details.
    if rate is None:
        state["next_action"] = NextAction.ASK_RATE
    else:
        # We've got a concrete rate from influencer → wait/acknowledge further messages
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE

    prompt = (
        "You are an AI assistant helping a brand negotiate with an influencer on WhatsApp.\n"
        f"The influencer's offered/confirmed rate (if detected from state) is: {rate}.\n\n"
        + WHATSAPP_CONFIRM_DETAILS_SUFFIX
    )

    agent_input = (
        history_to_agent_messages(history)
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
    state.setdefault("history", []).append(
        {
            "sender_type": "AI",
            "message": ai_reply,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    try:
        db = get_db()
        collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS
        )
        influencer_id = state.get("influencer_id")
        if influencer_id:
            payload = {
                "final_reply": state["final_reply"],
                "history": state["history"],
                "next_action": state["next_action"],
            }
            if rate is not None:
                try:
                    payload["last_offered_price"] = float(rate)
                except (TypeError, ValueError):
                    pass
            await collection.update_one(
                {"_id": ObjectId(influencer_id)},
                {"$set": payload},
            )
    except Exception as e:
        print(f"[confirm_details_node] Mongo persistence failed: {e}")

    return state
