from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.core.exception import NotFoundException
from app.db.connection import get_db
from app.utils.helpers import mongo_to_json
from bson import ObjectId

from app.utils.printcolors import Colors


async def FetchCampaignInfluencerInfo(_id: str):
    print(f"{Colors.GREEN}Entering into FetchCampaignInfluencerInfo")
    print("--------------------------------")
    print(f"{Colors.CYAN}Fetching campaign influencer info for: {_id}")
    print("--------------------------------")
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        projection = {
            "campaign_id": 1,
            "platform": 1,
            "pricing": 1,
            "max_price": 1,
            "min_price": 1,
        }

        data = await collection.find_one({"_id": ObjectId(_id)}, projection)
        print(f"{Colors.CYAN}Campaign Influencer data: {data}")
        print("--------------------------------")
        if not data:
            print(f"{Colors.RED}Campaign Influencer not found: {_id}")
            print("--------------------------------")
            raise NotFoundException(message=f"Campaign Influencer not found: {_id}")
        print(f"{Colors.YELLOW} Exiting from FetchCampaignInfluencerInfo")
        print("--------------------------------")
        return mongo_to_json(data)
    except Exception as e:
        print(f"{Colors.RED}Error in FetchCampaignInfluencerInfo: {e}")
        print("--------------------------------")
        raise NotFoundException(message=f"Campaign Influencer not found: {_id}")


async def fetch_pricing_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering fetch_pricing_node")
    print("--------------------------------")

    # Guardrail: Already fetched
    if state.get("min_price") and state.get("max_price"):
        print(f"{Colors.YELLOW}Pricing already present in state. Skipping DB fetch.")
        print("--------------------------------")
        return state

    # Guardrail: Ensure _id exists
    influencer_id = state.get("_id")
    if not influencer_id:
        raise ValueError("Missing campaign influencer _id in state")

    print(f"{Colors.CYAN}Fetching pricing for campaign influencer: {influencer_id}")
    print("--------------------------------")

    influencer = await FetchCampaignInfluencerInfo(influencer_id)

    min_price = influencer.get("min_price")
    max_price = influencer.get("max_price")

    # Validate pricing
    if min_price is None or max_price is None:
        raise ValueError("Pricing configuration missing in campaign influencer")

    if min_price > max_price:
        raise ValueError("Invalid pricing configuration: min_price > max_price")

    state["min_price"] = float(min_price)
    state["max_price"] = float(max_price)

    print(f"{Colors.GREEN}Pricing loaded → min: {min_price}, max: {max_price}")
    print("--------------------------------")

    return state
