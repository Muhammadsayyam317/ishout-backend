from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def price_escalation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into price_escalation_node")
    print("--------------------------------")

    min_price = state.get("min_price", 0)
    max_price = state.get("max_price", 0)
    last_price = state.get("last_offered_price")
    negotiation_round = state.get("negotiation_round", 0)

    # If no previous offer → start from max price
    if not last_price:
        next_price = max_price
    else:
        # Reduce toward min price (controlled decrement)
        decrement = (max_price - min_price) / 4  # 4 negotiation steps
        next_price = round(last_price - decrement, 2)

    # If reached or below min price → escalate to admin
    if next_price <= min_price:
        state["last_offered_price"] = min_price
        state["negotiation_round"] = negotiation_round + 1
        state["negotiation_status"] = "escalated"
        state["manual_negotiation"] = True
        state["final_reply"] = (
            "We’ve reached our best possible rate. Let me connect you with our team to explore further options."
        )
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION

        print(f"{Colors.RED} Min price reached → Escalating to admin")
        print("--------------------------------")
        return state

    # Continue negotiation
    state["last_offered_price"] = next_price
    state["negotiation_round"] = negotiation_round + 1
    state["negotiation_status"] = "pending"
    state["final_reply"] = (
        f"We can revise the offer to ${next_price:.2f}. Let us know if this works for you."
    )
    state["next_action"] = NextAction.ASK_RATE

    print(f"{Colors.CYAN} Offer adjusted to: {next_price}")
    print("--------------------------------")

    return state
