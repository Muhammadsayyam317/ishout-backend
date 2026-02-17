from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def counter_offer_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering handle_offer_node")
    print("--------------------------------")

    min_price = state.get("min_price", 0)
    max_price = state.get("max_price", 0)
    last_price = state.get("last_offered_price")
    offered = state.get("user_offer")

    # Start negotiation from min_price if no last offer
    if last_price is None:
        state["last_offered_price"] = min_price
        state["negotiation_round"] = 1
        state["final_reply"] = (
            f"Our initial offer for this campaign is ${min_price:.2f}. Let us know your thoughts."
        )
        state["next_action"] = NextAction.ASK_RATE
        print(f"{Colors.CYAN}Starting negotiation at min price: {min_price}")
        return state

    # Influencer offer received
    if offered is not None:
        if offered <= last_price:
            # Accept if their offer is lower than or equal to our current offer
            state["negotiation_status"] = "agreed"
            state["last_offered_price"] = offered
            state["final_reply"] = (
                f"Great! We confirm the collaboration at ${offered:.2f}."
            )
            state["next_action"] = NextAction.ACCEPT_NEGOTIATION
            state["user_offer"] = None
            print(f"{Colors.CYAN}Offer accepted: {offered}")
            return state

    # Incremental escalation by 20% of min_price
    next_price = last_price + round(min_price * 0.2, 2)
    if next_price > max_price:
        next_price = max_price
        state["negotiation_status"] = "escalated"
        state["manual_negotiation"] = True
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION
        state["final_reply"] = (
            "We've reached our maximum budget. Let me connect you with our team."
        )
        print(f"{Colors.RED}Max price reached → Escalating to admin")
    else:
        state["negotiation_status"] = "pending"
        state["next_action"] = NextAction.ASK_RATE
        state["final_reply"] = (
            f"We can revise the offer to ${next_price:.2f}. Let us know if this works for you."
        )
        print(f"{Colors.CYAN}Offer adjusted to: {next_price}")

    state["last_offered_price"] = next_price
    state["negotiation_round"] = state.get("negotiation_round", 1) + 1
    state["user_offer"] = None

    print(f"{Colors.YELLOW}Exiting handle_offer_node")
    print("--------------------------------")
    return state
