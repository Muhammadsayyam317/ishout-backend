from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState


def price_escalation_node(state: WhatsappNegotiationState):
    last_price = state.get("last_offered_price") or state.get("min_price") or 0
    max_price = state.get("max_price") or 0
    negotiation_round = state.get("negotiation_round", 0)

    next_price = round(last_price * 1.2, 2)

    if next_price >= max_price:
        state["admin_takeover"] = True
        state["final_reply"] = (
            "Thanks for your response. "
            "Let me loop in our team to discuss this further."
        )
        print(
            f"[price_escalation_node] Max price reached, escalating to admin. Next price: {next_price}"
        )
        return state

    state["last_offered_price"] = next_price
    state["negotiation_round"] = negotiation_round + 1

    state["final_reply"] = (
        f"We can improve the offer to ${next_price:.2f}. "
        "Let us know if this works for you."
    )

    print(
        f"[price_escalation_node] Offer escalated to {next_price}, round {state['negotiation_round']}"
    )
    return state
