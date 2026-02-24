from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db
from bson import ObjectId
from app.utils.printcolors import Colors


async def fetch_pricing_node(state: WhatsappNegotiationState, checkpointer=None):
    thread_id = state.get("thread_id")
    influencer_id = state.get("influencer_id")
    print("[DEBUG] influencer_id: ", influencer_id)
    print(f"{Colors.GREEN}Entering fetch_pricing_node")

    if state.get("min_price") and state.get("max_price"):
        return state

    # Guard: influencer_id must be present
    if not influencer_id:
        print(f"{Colors.RED}[fetch_pricing_node] Missing influencer_id in state")
        return state

    db = get_db()
    collection = db.get_collection("campaign_influencers")
    influencer = await collection.find_one(
        {"_id": ObjectId(influencer_id)},
        {"min_price": 1, "max_price": 1, "campaign_id": 1},
    )

    if not influencer:
        print(
            f"{Colors.RED}[fetch_pricing_node] Influencer not found for _id={influencer_id}"
        )
        return state

    state["min_price"] = float(influencer.get("min_price", 0))
    state["max_price"] = float(influencer.get("max_price", 0))
    state["campaign_id"] = influencer.get("campaign_id")

    if checkpointer:
        await checkpointer.save_checkpoint(
            key=f"negotiation:{thread_id}:pricing",
            value={"min_price": state["min_price"], "max_price": state["max_price"]},
            ttl=300,
        )
    return state
