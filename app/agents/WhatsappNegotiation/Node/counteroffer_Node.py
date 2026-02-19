from agents import Agent, Runner
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.Guardails.input_guardrails import WhatsappInputGuardrail
from app.utils.printcolors import Colors


async def counter_offer_node(state: WhatsappNegotiationState, checkpointer):
    print(f"{Colors.GREEN}Entering counter_offer_node")
    print("--------------------------------")
    thread_id = state.get("thread_id")

    min_price = state.get("min_price", 0)
    max_price = state.get("max_price", 0)
    last_price = state.get("last_offered_price")
    user_offer = state.get("user_offer")

    # Determine next offer
    if user_offer is not None and user_offer <= max_price:
        next_price = user_offer
        state["negotiation_status"] = "agreed"
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION
    else:
        if last_price is None:
            next_price = min_price
            state["negotiation_round"] = 1
        else:
            next_price = last_price + round(0.2 * min_price, 2)
            state["negotiation_round"] = state.get("negotiation_round", 1) + 1

        if next_price >= max_price:
            next_price = max_price
            state["negotiation_status"] = "escalated"
            state["manual_negotiation"] = True
            state["next_action"] = NextAction.ESCALATE_NEGOTIATION
        else:
            state["negotiation_status"] = "pending"
            state["next_action"] = NextAction.ASK_RATE

    state["last_offered_price"] = next_price
    state["user_offer"] = None

    # AI generates message dynamically
    prompt = f"Generate a WhatsApp negotiation reply with offered price ${next_price} and status {state['negotiation_status']}."
    result = await Runner.run(
        Agent(
            name="ai_counter_offer",
            instructions=prompt,
            input_guardrails=[WhatsappInputGuardrail],
            output_type=dict,
        ),
        input=state.get("history", []),
    )

    ai_message = result.final_output.get("final_reply", f"My offer is ${next_price}")
    state["final_reply"] = ai_message

    # Save last AI message in Redis for 5 min
    await checkpointer.save_checkpoint(
        key=f"negotiation:{thread_id}:last_message", value=ai_message, ttl=300
    )

    print(f"{Colors.CYAN}Counter Offer AI Message: {ai_message}")
    print(f"{Colors.YELLOW}Exiting counter_offer_node")
    print("--------------------------------")
    return state
