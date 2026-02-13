from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.core.exception import NotFoundException
from app.db.connection import get_db
from app.utils.helpers import mongo_to_json
from bson import ObjectId


async def FetchCampaignInfluencerInfo(_id: str):
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
    return mongo_to_json(data)


async def fetch_pricing_node(state: WhatsappNegotiationState):
    influencer = await FetchCampaignInfluencerInfo(state["_id"])

    state["min_price"] = influencer["min_price"]
    state["max_price"] = influencer["max_price"]

    return state
