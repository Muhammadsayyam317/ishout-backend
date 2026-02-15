from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def price_escalation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into price_escalation_node")
    print("--------------------------------")
    last_price = state.get("last_offered_price", state.get("min_price", 0))
    max_price = state.get("max_price", 0)
    negotiation_round = state.get("negotiation_round", 0)

    # Calculate next offer (20% increase)
    next_price = round(last_price * 1.2, 2)
    if next_price >= max_price:
        # Max reached → admin takeover
        state["final_reply"] = (
            "Thanks for your response. Let me loop in our team to discuss this further."
        )
        state["negotiation_status"] = "escalated"
        state["last_offered_price"] = max_price
        state["negotiation_round"] = negotiation_round + 1
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION  # admin handles next
        state["manual_negotiation"] = True
        print(
            f"{Colors.CYAN} [price_escalation_node] Max price reached, escalating to admin. Next price: {next_price}"
        )
        return state

    # Continue escalation
    state["last_offered_price"] = next_price
    state["negotiation_round"] = negotiation_round + 1
    state["negotiation_status"] = "pending"
    state["final_reply"] = (
        f"We can improve the offer to ${next_price:.2f}. Let us know if this works for you."
    )
    state["next_action"] = NextAction.ASK_RATE
    print(f"{Colors.CYAN} [price_escalation_node] Offer escalated: {next_price}")
    print(f"{Colors.YELLOW} Exiting from price_escalation_node")
    print("--------------------------------")
    return state
