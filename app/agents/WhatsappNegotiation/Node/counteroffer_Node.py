from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import CounterOfferOutput, NextAction
from app.utils.printcolors import Colors
from app.utils.prompts import WHATSAPP_COUNTER_OFFER_RULES
from app.utils.message_context import (
    get_history_list,
    set_history_list,
    history_to_agent_messages,
)


async def counter_offer_node(state: WhatsappNegotiationState, checkpointer=None):
    print(f"{Colors.GREEN}Entering counter_offer_node")
    print("--------------------------------")
    thread_id = state.get("thread_id")
    min_price = state.get("min_price") or 0
    max_price = state.get("max_price") or 0
    last_price = state.get("last_offered_price")
    user_offer = state.get("user_offer")
    negotiation_round = state.get("negotiation_round") or 0

    if not min_price or not max_price:
        print(
            f"{Colors.RED}[counter_offer_node] min_price={min_price}, max_price={max_price} — pricing not loaded, skipping"
        )
        state["final_reply"] = (
            "Thanks for your interest! Let me get some details together and get back to you shortly."
        )
        return state

    # If we've already escalated (hit our max offer before), don't keep
    # re-sending higher prices. Send a handoff-style message.
    if state.get("negotiation_status") == "escalated" and last_price == max_price:
        print(
            f"{Colors.YELLOW}[counter_offer_node] Already escalated at max_price={max_price} → sending review/hand-off message"
        )
        handoff_message = (
            "We've already shared the best rate we can offer at the moment. "
            "We'll review this internally and get back to you if we can adjust anything further."
        )
        state["final_reply"] = handoff_message
        state["manual_negotiation"] = True
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE
        hist = get_history_list(state)
        set_history_list(state, hist)
        state["history"].append({"sender_type": "AI", "message": handoff_message})
        if checkpointer:
            await checkpointer.save_checkpoint(
                key=f"negotiation:{thread_id}:last_message",
                value=handoff_message,
                ttl=300,
            )
        return state

    new_round = negotiation_round + 1

    # Build context for the AI to decide both the price and the message
    context_lines = [
        "You are a professional negotiator representing a brand, chatting with an influencer on WhatsApp.",
        "",
        "PRICING CONTEXT:",
        f"- Minimum the brand can offer: ${min_price:.2f}",
        f"- Maximum the brand can go up to: ${max_price:.2f}",
        f"- Brand's last offered price: {'${:.2f}'.format(last_price) if last_price is not None else 'None (this is the first offer)'}",
        f"- Influencer's proposed rate (if any): {'${:.2f}'.format(user_offer) if user_offer is not None else 'None (they have not named a specific number)'}",
        f"- Negotiation round: {new_round}",
    ]

    prompt = "\n".join(context_lines) + "\n\n" + WHATSAPP_COUNTER_OFFER_RULES

    history = get_history_list(state)
    set_history_list(state, history)
    if history:
        agent_input = history_to_agent_messages(history)
    if not history or not agent_input:
        agent_input = (
            f"Brand is negotiating a collaboration rate with an influencer. "
            f"Range: ${min_price:.2f}–${max_price:.2f}. Generate an appropriate offer and message."
        )

    result = await Runner.run(
        Agent(
            name="ai_counter_offer",
            instructions=prompt,
            input_guardrails=[],
            output_type=AgentOutputSchema(
                CounterOfferOutput, strict_json_schema=False
            ),
        ),
        input=agent_input,
    )

    raw_output = result.final_output or {}
    ai_price = raw_output.get("offered_price")
    ai_message = raw_output.get("final_reply", "")

    # --- Hard guardrails: clamp AI's chosen price to [min, max] and never go backward ---
    try:
        ai_price = float(ai_price)
    except (TypeError, ValueError):
        ai_price = last_price if last_price is not None else min_price

    ai_price = max(ai_price, min_price)
    ai_price = min(ai_price, max_price)
    if last_price is not None:
        ai_price = max(ai_price, last_price)
    ai_price = round(ai_price, 2)

    if not ai_message:
        ai_message = f"We can offer you ${ai_price:.2f} for this collaboration. Let us know what you think!"

    # Update state
    state["last_offered_price"] = ai_price
    state["negotiation_round"] = new_round
    state["user_offer"] = None

    if ai_price >= max_price:
        state["negotiation_status"] = "escalated"
        state["manual_negotiation"] = True
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION
    else:
        state["negotiation_status"] = "pending"
        state["next_action"] = NextAction.ASK_RATE

    state["final_reply"] = ai_message
    state["history"].append({"sender_type": "AI", "message": ai_message})

    if checkpointer:
        await checkpointer.save_checkpoint(
            key=f"negotiation:{thread_id}:last_message", value=ai_message, ttl=300
        )

    print(
        f"{Colors.CYAN}[counter_offer_node] AI chose price=${ai_price:.2f} "
        f"(min={min_price}, max={max_price}, last={last_price}, user_offer={user_offer})"
    )
    return state
