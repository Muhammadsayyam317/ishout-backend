import httpx
from pymongo.collection import ObjectId
from app.config.credentials_config import config
from app.db.connection import get_db
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.utils.Enums.user_enum import SenderType
from bson.errors import InvalidId
from datetime import datetime, timezone
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    update_negotiation_state,
)

# Template – will be formatted with the influencer's name.
INITIAL_OUTREACH_MESSAGE = (
    "Hi {name}, We're reaching out from iShout regarding an upcoming brand campaign\n\n"
    "We'd love to work with you on an upcoming brand campaign where you'd create social media content "
    "such as posts and stories to promote the brand.\n\n"
    "If that sounds interesting, just reply 'interested' and we can discuss your rate, share more details, or feel free to ask any questions."
)


async def NegotiationInitialMessage(influencer_id: str):
    db = get_db()
    collection = db.get_collection("campaign_influencers")
    try:
        influencer_object_id = ObjectId(influencer_id)
    except InvalidId:
        return {"status": "error", "message": "Invalid influencer_id"}
    influencer = await collection.find_one({"_id": influencer_object_id})
    if not influencer:
        return {"status": "error", "message": "Influencer not found"}

    campaign_id = influencer.get("campaign_id")
    brand_thread_id = None
    campaign_logo_url = None
    if campaign_id:
        try:
            campaigns_collection = db.get_collection(
                config.MONGODB_ATLAS_COLLECTION_CAMPAIGNS
            )
            briefs_collection = db.get_collection(
                config.MONGODB_CAMPAIGN_BRIEF_GENERATION
            )
            camp_oid = (
                campaign_id
                if isinstance(campaign_id, ObjectId)
                else ObjectId(str(campaign_id))
            )
            campaign = await campaigns_collection.find_one(
                {"_id": camp_oid},
                {"brand_thread_id": 1, "brief_id": 1},
            )
            if campaign:
                brand_thread_id = campaign.get("brand_thread_id")
                brief_id = campaign.get("brief_id")
                if brief_id:
                    briefs = await briefs_collection.find(
                        {"_id": {"$in": [str(brief_id)]}}
                    ).to_list(length=None)
                    brief_logo_map = {
                        str(doc["_id"]): (doc.get("response") or {}).get(
                            "campaign_logo_url"
                        )
                        for doc in briefs
                    }
                    campaign_logo_url = brief_logo_map.get(str(brief_id))
        except (InvalidId, TypeError, ValueError) as e:
            print(
                f"[NegotiationInitialMessage] Could not resolve campaign / brief fields: {e}"
            )

    influencer_name = influencer.get("username")
    phone_number = influencer.get("phone_number")

    if not phone_number:
        return {"status": "error", "message": "Influencer has no phone number"}

    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    payload_meta = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "negotiation",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": influencer_name},
                    ],
                }
            ],
        },
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload_meta,
            )
    except Exception as e:
        print(f"[NegotiationInitialMessage] Error sending WhatsApp message: {e}")
        return {"status": "error", "message": f"Error sending WhatsApp message: {e}"}

    # Personalize the stored message with the influencer's name
    personalized_message = INITIAL_OUTREACH_MESSAGE.format(name=influencer_name or "")

    await save_negotiation_message(
        thread_id=phone_number,
        username=influencer_name,
        sender=SenderType.AI.value,
        message=personalized_message,
        agent_paused=False,
        human_takeover=False,
        conversation_mode="NEGOTIATION",
    )
    # Create Negotiation Control Record with fresh history containing the initial outreach
    await update_negotiation_state(
        thread_id=phone_number,
        data={
            "thread_id": phone_number,
            "influencer_id": influencer_id,
            "campaign_id": campaign_id,
            "brand_thread_id": brand_thread_id,
            "campaign_logo_url": campaign_logo_url,
            "analysis": {},
            "final_reply": None,
            "intent": None,
            "next_action": None,
            "min_price": None,
            "max_price": None,
            "last_offered_price": None,
            "negotiation_round": 0,
            "negotiation_status": None,
            "manual_negotiation": False,
            "user_offer": None,
            "negotiation_completed": False,
            "admin_approved": None,
            "Brand_approved": None,
            "conversation_mode": "NEGOTIATION",
            "agent_paused": False,
            "human_takeover": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "history": [
                {
                    "sender_type": "AI",
                    "message": personalized_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            ],
        },
    )
    return {
        "status": "success",
        "message": "Negotiation Initial Message sent successfully",
    }
