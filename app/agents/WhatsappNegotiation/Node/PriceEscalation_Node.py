from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def price_escalation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into price_escalation_node")
    print("--------------------------------")
    last_price = state.get("last_offered_price") or state.get("min_price") or 0
    max_price = state.get("max_price") or 0
    negotiation_round = state.get("negotiation_round", 0)

    next_price = round(last_price * 1.2, 2)

    if next_price >= max_price:
        state["admin_takeover"] = True
        state["final_reply"] = (
            "Thanks for your response. Let me loop in our team to discuss this further."
        )
        state["next_action"] = (
            NextAction.ACCEPT_NEGOTIATION
        )  # influencer must accept admin's next step
        print(
            f"{Colors.CYAN}[price_escalation_node] Max price reached, escalating to admin. Next price: {next_price}"
        )
        return state

    state["last_offered_price"] = next_price
    state["negotiation_round"] = negotiation_round + 1
    state["final_reply"] = (
        f"We can improve the offer to ${next_price:.2f}. Let us know if this works for you."
    )
    state["next_action"] = NextAction.ASK_RATE

    print(
        f"{Colors.CYAN}[price_escalation_node] Offer escalated to {next_price}, round {state['negotiation_round']}"
    )
    print(f"{Colors.YELLOW} Exiting from price_escalation_node")
    print("--------------------------------")
    return state
