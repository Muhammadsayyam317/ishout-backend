from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.agents.WhatsappNegotiation.Node.PriceEscalation_Node import (
    price_escalation_node,
)
from app.utils.printcolors import Colors


def counter_offer_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into counter_offer_node")
    print("--------------------------------")
    offered = state.get("analysis", {}).get("budget_amount")
    max_price = state.get("max_price") or 0

    if offered is None:
        print("[counter_offer_node] No budget amount provided by influencer.")
        state["final_reply"] = "Could you please share your expected budget?"
        return state

    if offered <= max_price:
        state["final_reply"] = (
            f"That works for us 👍 Let’s proceed with ${offered:.2f}."
        )
        state["last_offered_price"] = offered
        state["admin_takeover"] = False
        print(f"[counter_offer_node] Offer accepted: {offered}")
        return state

    print(
        f"[counter_offer_node] Offer {offered} exceeds max {max_price}, escalating..."
    )
    print(f"{Colors.YELLOW} Escalating price for campaign influencer: {state['_id']}")
    print("--------------------------------")
    return price_escalation_node(state)
