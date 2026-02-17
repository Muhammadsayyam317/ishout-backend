from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def counter_offer_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering counter_offer_node")
    print("--------------------------------")

    min_price = state.get("min_price", 0)
    max_price = state.get("max_price", 0)
    last_price = state.get("last_offered_price")
    user_offer = state.get("user_offer")

    if last_price is None:
        next_price = min_price
        state["negotiation_round"] = 1
        print(f"{Colors.CYAN}Starting negotiation at min price: {next_price}")
    else:
        next_price = last_price + round(0.2 * min_price, 2)
        state["negotiation_round"] = state.get("negotiation_round", 1) + 1

    if next_price >= max_price:
        next_price = max_price
        state["negotiation_status"] = "escalated"
        state["manual_negotiation"] = True
        state["next_action"] = NextAction.ESCALATE_NEGOTIATION
        state["final_reply"] = (
            f"We've reached our maximum budget of ${next_price:.2f}. Connecting you with our team."
        )
        print(f"{Colors.RED}Max price reached → Escalating to admin")
    else:
        state["negotiation_status"] = "pending"
        state["next_action"] = NextAction.ASK_RATE
        state["final_reply"] = (
            f"We can revise the offer to ${next_price:.2f}. Does this work for you?"
        )
        print(f"{Colors.CYAN}Offer adjusted to: {next_price}")
    if user_offer is not None and user_offer <= next_price:
        state["negotiation_status"] = "agreed"
        state["last_offered_price"] = user_offer
        state["final_reply"] = (
            f"Great! We confirm the collaboration at ${user_offer:.2f}."
        )
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION
        print(f"{Colors.CYAN}Influencer offer accepted: {user_offer}")
    else:
        state["last_offered_price"] = next_price
    state["user_offer"] = None

    print(f"{Colors.YELLOW}Exiting counter_offer_node")
    print("--------------------------------")
    return state
