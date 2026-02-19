from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.db.connection import get_db
from bson import ObjectId
from app.utils.printcolors import Colors


async def fetch_pricing_node(state: WhatsappNegotiationState, checkpointer):
    thread_id = state.get("thread_id")
    influencer_id = state.get("_id")
    print(f"{Colors.GREEN}Entering fetch_pricing_node")
    print("--------------------------------")

    if not influencer_id:
        raise ValueError("Missing campaign influencer _id in state")

    # If pricing already in state, skip DB
    if state.get("min_price") and state.get("max_price"):
        print(f"{Colors.YELLOW}Pricing already in state, skipping DB fetch.")
        return state

    db = get_db()
    collection = db.get_collection("campaign_influencers")
    influencer = await collection.find_one(
        {"_id": ObjectId(influencer_id)},
        {"min_price": 1, "max_price": 1, "campaign_id": 1},
    )
    if not influencer:
        raise ValueError(f"Campaign influencer not found: {influencer_id}")

    state["min_price"] = float(influencer["min_price"])
    state["max_price"] = float(influencer["max_price"])
    state["campaign_id"] = influencer["campaign_id"]

    # Save pricing to Redis for 5 min
    await checkpointer.save_checkpoint(
        key=f"negotiation:{thread_id}:pricing",
        value={"min_price": state["min_price"], "max_price": state["max_price"]},
        ttl=300,
    )

    print(
        f"{Colors.CYAN}Pricing loaded → min: {state['min_price']}, max: {state['max_price']}"
    )
    print(f"{Colors.YELLOW}Exiting fetch_pricing_node")
    print("--------------------------------")
    return state
