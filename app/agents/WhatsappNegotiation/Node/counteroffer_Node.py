from agents import Agent, Runner
from agents.agent_output import AgentOutputSchema
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import GenerateReplyOutput, NextAction
from app.utils.printcolors import Colors
from app.utils.prompts import WHATSAPP_COUNTER_OFFER_RULES


async def counter_offer_node(state: WhatsappNegotiationState, checkpointer=None):
    print(f"{Colors.GREEN}Entering counter_offer_node")
    print("--------------------------------")
    thread_id = state.get("thread_id")
    min_price = state.get("min_price") or 0
    max_price = state.get("max_price") or 0
    last_price = state.get("last_offered_price")
    user_offer = state.get("user_offer")

    if not min_price or not max_price:
        print(
            f"{Colors.RED}[counter_offer_node] min_price={min_price}, max_price={max_price} — pricing not loaded, skipping"
        )
        state["final_reply"] = (
            "Thanks for your interest! Let me get some details together and get back to you shortly."
        )
        return state

    # If we've already escalated (hit our max offer before), don't keep
    # re-sending higher prices. Instead, send a handoff-style message.
    if state.get("negotiation_status") == "escalated" and state.get(
        "last_offered_price"
    ) == max_price:
        print(
            f"{Colors.YELLOW}[counter_offer_node] Already escalated at max_price={max_price} → sending review/hand-off message"
        )
        handoff_message = (
            "We’ve already shared the best rate we can offer at the moment. "
            "We’ll review this internally and get back to you if we can adjust anything further."
        )
        state["final_reply"] = handoff_message
        state["manual_negotiation"] = True
        # After this, further messages should go through a non-pricing path
        state["next_action"] = NextAction.WAIT_OR_ACKNOWLEDGE
        state.setdefault("history", []).append(
            {"sender_type": "AI", "message": handoff_message}
        )
        if checkpointer:
            await checkpointer.save_checkpoint(
                key=f"negotiation:{thread_id}:last_message",
                value=handoff_message,
                ttl=300,
            )
        return state

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

    # Build a single prompt that encodes the situation (first offer vs counter)
    user_offer = state.get("user_offer")
    negotiation_round = state.get("negotiation_round", 1)
    has_user_offer = user_offer is not None

    context_lines = [
        "You are an AI assistant negotiating on behalf of a brand with an influencer on WhatsApp.",
        f"Negotiation round: {negotiation_round}.",
        f"Brand's current offer to the influencer: ${next_price:.2f}",
        f"Allowed price range for this influencer: ${min_price:.2f}–${max_price:.2f}.",
    ]

    if has_user_offer:
        context_lines.append(
            f"The influencer has previously proposed a rate of ${user_offer:.2f}"
        )
    else:
        context_lines.append(
            "The influencer has not proposed any price yet; they have only expressed interest in collaborating."
        )

    rules = WHATSAPP_COUNTER_OFFER_RULES.replace("${offer}", f"${next_price:.2f}")

    prompt = "\n".join(context_lines) + "\n\n" + rules

    # Ensure we always provide a non-empty input to the agent.
    history = state.get("history", [])
    if history:
        agent_input = history
    else:
        # First turn: send a simple textual input instead of an empty list
        agent_input = (
            f"Brand is sending an offer of ${next_price:.2f} to an interested influencer. "
            "Generate a natural WhatsApp message for this situation."
        )

    result = await Runner.run(
        Agent(
            name="ai_counter_offer",
            instructions=prompt,
            input_guardrails=[],
            output_type=AgentOutputSchema(
                GenerateReplyOutput, strict_json_schema=False
            ),
        ),
        input=agent_input,
    )
    ai_message = result.final_output.get("final_reply", f"My offer is ${next_price}")
    state["final_reply"] = ai_message
    state.setdefault("history", []).append({"sender_type": "AI", "message": ai_message})

    if checkpointer:
        await checkpointer.save_checkpoint(
            key=f"negotiation:{thread_id}:last_message", value=ai_message, ttl=300
        )

    return state
