from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.core.exception import NotFoundException
from app.db.connection import get_db
from app.utils.helpers import mongo_to_json
from bson import ObjectId

from app.utils.printcolors import Colors


async def FetchCampaignInfluencerInfo(_id: str):
    print(f"{Colors.GREEN}Entering into FetchCampaignInfluencerInfo")
    print("--------------------------------")
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        projection = {
            "username": 1,
            "campaign_id": 1,
            "platform": 1,
            "phone_number": 1,
            "pricing": 1,
            "max_price": 1,
            "min_price": 1,
        }

        data = await collection.find_one({"_id": ObjectId(_id)}, projection)
        if not data:
            raise NotFoundException(message=f"Campaign Influencer not found: {_id}")
            print(f"{Colors.CYAN}Campaign Influencer found: {_id}")
            print("--------------------------------")
        return mongo_to_json(data)
    except Exception as e:
        print(f"{Colors.RED}Error in FetchCampaignInfluencerInfo: {e}")
        print("--------------------------------")
        raise NotFoundException(message=f"Campaign Influencer not found: {_id}")


async def fetch_pricing_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Fetching pricing for campaign influencer: {state['_id']}")
    print("--------------------------------")
    influencer = await FetchCampaignInfluencerInfo(state["_id"])
    print(f"{Colors.CYAN}Pricing fetched for campaign influencer: {state['_id']}")
    print("--------------------------------")
    state["min_price"] = influencer["min_price"]
    state["max_price"] = influencer["max_price"]
    print(f"{Colors.GREEN} Exiting from fetch_pricing_node")
    print("--------------------------------")

    return state
