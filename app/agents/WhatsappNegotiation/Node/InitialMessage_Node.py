import httpx
from pymongo.collection import ObjectId
from app.config.credentials_config import config
from app.db.connection import get_db
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.utils.Enums.user_enum import SenderType
from bson.errors import InvalidId


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
    print("Payload Meta: ", payload_meta)
    print("--------------------------------")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload_meta,
            )
        print("--------------------------------")
        print("Response: ", response.json())
        print("--------------------------------")
    except Exception as e:
        print(f"[NegotiationInitialMessage] Error sending WhatsApp message: {e}")
        return {"status": "error", "message": f"Error sending WhatsApp message: {e}"}

    await save_negotiation_message(
        thread_id=phone_number,
        username=influencer_name,
        sender=SenderType.AI.value,
        message="""Hi this is the collaboration team from iShout.\n\nWe’d love to work with you on an upcoming campaign that matches your profile.\n\nJust reply 'interested,' and we will share the campaign brief and next steps.""",
        agent_paused=False,
        human_takeover=False,
        conversation_mode="NEGOTIATION",
    )
    return {"status": "success"}
