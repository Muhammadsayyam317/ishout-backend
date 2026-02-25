from app.Schemas.instagram.negotiation_schema import NextAction
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from app.db.connection import get_db
from bson import ObjectId


async def accept_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering accept_negotiation_node")
    print("--------------------------------")

    state["negotiation_status"] = "agreed"
    state["negotiation_completed"] = True
    final_price = state.get("last_offered_price")
    if final_price is None:
        final_price_text = ""
    else:
        final_price_text = f" at ${final_price:.2f}"

    state["final_reply"] = (
        f"Great! We're happy to proceed{final_price_text}. "
        "We'll share next steps shortly."
    )
    state["next_action"] = NextAction.CLOSE_CONVERSATION

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "negotiation_status": state["negotiation_status"],
                    "negotiation_completed": True,
                    "final_reply": state["final_reply"],
                    "last_offered_price": state.get("last_offered_price"),
                    "next_action": state["next_action"],
                }
            },
        )
    except Exception as e:
        print(f"[accept_negotiation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}Negotiation accepted. Reply: {state['final_reply']}")
    print(f"{Colors.YELLOW}Exiting from accept_negotiation_node")
    print("--------------------------------")
    return state
