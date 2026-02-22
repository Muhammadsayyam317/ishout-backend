from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from app.db.connection import get_db
from bson import ObjectId


async def reject_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering reject_negotiation_node")
    print("--------------------------------")
    state["negotiation_status"] = "rejected"
    state["final_reply"] = (
        "Thanks for your time! We understand this isn’t a fit at the moment. "
        "We’ll keep you in mind for future campaigns."
    )
    state["next_action"] = None

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "negotiation_status": state["negotiation_status"],
                    "final_reply": state["final_reply"],
                    "next_action": state["next_action"],
                }
            },
        )
    except Exception as e:
        print(f"[reject_negotiation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}[reject_negotiation_node] Negotiation rejected")
    print(f"{Colors.YELLOW}Exiting reject_negotiation_node")
    print("--------------------------------")

    return state
