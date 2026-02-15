from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.Schemas.instagram.negotiation_schema import NextAction
from app.utils.printcolors import Colors


def counter_offer_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into counter_offer_node")
    print("--------------------------------")
    min_price = state.get("min_price", 0)
    max_price = state.get("max_price", 0)
    offered = state.get("analysis", {}).get("budget_amount")

    if offered is None:
        state["final_reply"] = "Could you please share your expected budget?"
        state["next_action"] = NextAction.ASK_RATE
        print(
            f"{Colors.CYAN} [counter_offer_node] No budget amount provided by influencer."
        )
        return state

    # Offer within max → accept
    if offered <= max_price:
        state["final_reply"] = (
            f"That works for us 👍 Let’s proceed with ${offered:.2f}."
        )
        state["last_offered_price"] = offered
        state["negotiation_round"] = state.get("negotiation_round", 0)
        state["next_action"] = NextAction.ACCEPT_NEGOTIATION
        state["negotiation_status"] = "agreed"
        print(f"{Colors.CYAN} [counter_offer_node] Offer accepted: {offered}")
        return state

    # Offer exceeds max → escalate
    state["last_offered_price"] = max(
        min_price, state.get("last_offered_price", min_price)
    )
    print(
        f"{Colors.CYAN} [counter_offer_node] Offer escalated: {state['last_offered_price']}"
    )
    state["negotiation_round"] = state.get("negotiation_round", 0)
    state["next_action"] = NextAction.ESCALATE_NEGOTIATION
    state["negotiation_status"] = "escalated"
    print(f"{Colors.YELLOW} Exiting from counter_offer_node")
    print("--------------------------------")
    return state
